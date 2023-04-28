# Code creating random events all over the visual field simulating coherent motion

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random

# os.system('cls')
matplotlib.use('TkAgg')

# camera resolution
width = 50
height = 50

t = np.arange(0, 1, 0.1)  # s
pol = 1
events_percentage = 75  # % percentage of the total number of possible events to occur at each timestamp
num_events = round(height * width * events_percentage / 100)  # number of occurring events at each timestamp

events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
frame = np.zeros((width, height))
coordinates = np.zeros((width * height, 2), dtype=int)  # list of all pixel coordinates
idx = 0
for x in np.arange(width):
    for y in np.arange(height):
        coordinates[idx][0] = x
        coordinates[idx][1] = y
        idx += 1

plt.figure()
for ts in t:
    coor_idx = np.random.choice(len(coordinates), size=num_events, replace=False)
    coor_sample = coordinates[coor_idx]
    for i in np.arange(len(coor_sample)):
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        # creating events
        # x
        events['x'].append(coor_sample[i][0])
        # y
        events['y'].append(coor_sample[i][1])
        # ts
        events['ts'].append(ts)
        # pol
        events['pol'].append(pol)
        # idx
        events['idx'].append(coor_sample[i][0] * height + coor_sample[i][1])
        frame[coor_sample[i][1], coor_sample[i][0]] = 1

 # Visualization
    plt.imshow(frame)
    plt.draw()
    plt.pause(0.1)
    frame = np.zeros((width, height))

np.save("events.npy", events)
