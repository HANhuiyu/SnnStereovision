import urllib
import numpy as np

# This class reads spikes from an external input source (url or local file) and preprocesses the spikes for the retinas
# The spikes should be stored in a file with an extension ".dat" and should be formatted as follows:
# spike_time position_x position_y polarity retina
# where spike_time is in microseconds, position_x and position_y are pixel coordinates in the range [1, dim_x(dim_y)]
# polarity is the event type (0 OFF, 1 ON) and retina is the retina ID (0 left, 1 right) (or the other way round :D)

import tables
import hdf5plugin
import h5py
import numpy as np
import pandas as pd

#file_path= 'event_h5'
#sim_time = 100 # in millisecond

class ExternalHdf5InputReader():
    def __init__(self, url="",
                 file_path="",
                 crop_xmin=-1,
                 crop_ymin=-1,
                 crop_xmax=-1,
                 crop_ymax=-1,
                 dim_x=1,
                 dim_y=1,
                 sim_time=1000,
                 is_rawdata_time_in_ms=False):
        # these are the attributes which contain will contain the sorted, filtered and formatted spikes for each pixel
        self.retinaLeft = []
        self.retinaRight = []

        if url is not "" and file_path is not "" or \
            url is "" and file_path is "":
            print("ERROR: Ambiguous or void input source address. Give either a URL or a local file path.")
            return

	if file_path is not "" and file_path[-3:] == "_h5":
		file_left_event = file_path + '/left_events.h5'
		h5f_left = h5py.File(file_left_event, "r")
		
		events_left = dict()
		
		for dset_str in ['p', 'x', 'y', 't']:
		   events_left[dset_str] = h5f_left['events/{}'.format(dset_str)]

		ms_to_idx_left = np.asarray(h5f_left['ms_to_idx'], dtype='int64')

		file_right_event = file_path + '/right_events.h5'
		h5f_right = h5py.File(file_right_event, "r")

		events_right = dict()

		for dset_str in ['p', 'x', 'y', 't']:
		   events_right[dset_str] = h5f_right['events/{}'.format(dset_str)]

		ms_to_idx_right = np.asarray(h5f_right['ms_to_idx'], dtype='int64')
		



        # initialise the maximum time constant as the total simulation duration. This is needed to set a value
        # for pixels which don't spike at all, since the pyNN frontend requires so.
        # If they spike at the last possible time step, their firing will have no effect on the simulation.
        max_time = sim_time

        # containers for the formatted spikes
        # define as list of lists of lists so that SpikeSourceArrays don't complain
        retinaL = [[[] for y in range(dim_y)] for x in range(dim_x)]
        retinaR = [[[] for y in range(dim_y)] for x in range(dim_x)]

        # last time a spike has occured for a pixel -- used to filter event bursts
	# here, i don't think so han 06/05/2020
	'''
        last_tL = [[0.0]]
        last_tR = [[0.0]]
        for x in range(0, dim_x):
            for y in range(0, dim_y):
                last_tL[x].append(-1.0)
                last_tR[x].append(-1.0)
            last_tL.append([])
            last_tR.append([])
	'''
	last_tL =  [[[] for y in range(dim_y)] for x in range(dim_x)]
	last_tR =  [[[] for y in range(dim_y)] for x in range(dim_x)]
	for x in range(0, dim_x):
	    for y in range(0, dim_y):
		last_tL[x][y].append(-1.0)
		last_tR[x][y].append(-1.0)
	last_tL=np.array(last_tL)
	last_tR=np.array(last_tR)
	
        # process each event in the event list and format the time and position. Distribute among the retinas respectively
        index_left=ms_to_idx_left[sim_time]
	index_right=ms_to_idx_right[sim_time]
		
	print("index_left is",index_left)
	print("index_right is",index_right)

	for i in range(0,index_left):
		
		x = events_left['x'][i]
		y = events_left['y'][i]
		t = events_left['t'][i]/1000 # convert the microsecond to millisecond

		if crop_xmax >= 0 and crop_xmin >= 0 and crop_ymax >= 0 and crop_ymin >= 0:
		        if crop_xmin <= x < crop_xmax and crop_ymin <= y < crop_ymax:
		            
		        # filter event bursts and limit the events to the maximum time for the simulation
				if t - last_tL[x - crop_xmin][y - crop_ymin] >= 1.0 and t <= max_time:
				    # print "r", x, y, x-lowerBoundX, y-lowerBoundY
				    retinaL[x - crop_xmin][y - crop_ymin].append(t)
				    last_tL[x - crop_xmin][y - crop_ymin] = t
	for i in range(0,index_right):
	
		x = events_right['x'][i]
		y = events_right['y'][i]
		t = events_right['t'][i]/1000 # convert the microsecond to millisecond

		if crop_xmax >= 0 and crop_xmin >= 0 and crop_ymax >= 0 and crop_ymin >= 0:
		        if crop_xmin <= x < crop_xmax and crop_ymin <= y < crop_ymax:
		            
		        # filter event bursts and limit the events to the maximum time for the simulation
				if t - last_tR[x - crop_xmin][y - crop_ymin] >= 1.0 and t <= max_time:
				    # print "r", x, y, x-lowerBoundX, y-lowerBoundY
				    retinaR[x - crop_xmin][y - crop_ymin].append(t)
				    last_tR[x - crop_xmin][y - crop_ymin] = t

        # fill the void cells with the last time possible, which has no effect on the simulation. The SpikeSourceArray
        # requires a value for each cell.
        for y in range(0, dim_x):
            for x in range(0, dim_y):
                if retinaR[y][x] == []:
                    retinaR[y][x].append(max_time + 10)
                if retinaL[y][x] == []:
                    retinaL[y][x].append(max_time + 10)

        # store the formatted and filtered events which are to be passed to the retina constructors
        self.retinaLeft = retinaL
        self.retinaRight = retinaR

	'''
	print('hello han here for the spikearray')
	print(len(retinaL))
	print(len(retinaL[1]))
	print(len(retinaL[1][1]))
	print('the spike arrary of the retinal is ', retinaL)
	print('bonjour,han finir the print of the spikearray')
	'''


