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


sim_time = 10000 # in ms

class ExternalHdf5InputReader():
    def __init__(self,
                 file_path,
                 #crop_xmin=-1,
                 #crop_ymin=-1,
                 #crop_xmax=-1,
                 #crop_ymax=-1,
                 dim_x=1,
                 dim_y=1,
                 sim_time=1000,
                 is_rawdata_time_in_ms=False):
        # these are the attributes which contain will contain the sorted, filtered and formatted spikes for each pixel
        self.retinaLeft = []
        self.retinaRight = []
        print(file_path)

        if file_path is not "":
            eventList_left=list()
            with open(file_path["left"], 'r') as events_left:
                is_data = False
                for line in events_left:
                    # skip preambles and other logged information
                    if not "DATA START" in line and not "DATA END" in line:
                        if not is_data:
                            continue
                        else:
                            l = line.split()
                            eventList_left.append([ int(l[0]), int(l[1]),float(l[2])])

                    else:
                        is_data = True
            eventList_right=list()
            with open(file_path["right"], 'r') as events_right:
                is_data = False
                for line in events_right:
                    # skip preambles and other logged information
                    if not "DATA START" in line and not "DATA END" in line:
                        if not is_data:
                            continue
                        else:
                            l = line.split()
                            eventList_right.append([ int(l[0]), int(l[1]),float(l[2])])

                    else:
                        is_data = True

        max_time = sim_time

        retinaL = [[[] for y in range(dim_y)] for x in range(dim_x)]
        retinaR = [[[] for y in range(dim_y)] for x in range(dim_x)]

        for event in eventList_left:
            x = event[0]
            y = event[1]
            t = event[2]
            retinaL[x][y].append(t)

        for event in eventList_right:
            x = event[0]
            y = event[1]
            t = event[2]
            retinaR[x][y].append(t)

        for x in range(0, dim_x):
            for y in range(0, dim_y):
                if retinaR[x][y] == []:
                    retinaR[x][y].append(max_time + 10)
                if retinaL[x][y] == []:
                    retinaL[x][y].append(max_time + 10)

        self.retinaLeft = retinaL
        self.retinaRight = retinaR
