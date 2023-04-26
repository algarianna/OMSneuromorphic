# Code creating random events all over the visual field simulating coherent motion

import array
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random
from tempfile import TemporaryFile
import time
import os

# os.system('cls')
matplotlib.use('TkAgg')

# camera resolution
width = 50
height = 50


t = np.arange(0, 1, 0.1) # s
pol = 1
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
frame = np.zeros((width, height))
plt.figure()
num_e = 2000

for ts in t:
    x_sample = np.random.choice(np.arange(width), size = 2000)
    y_sample = np.random.choice(np.arange(height), size = 2000)
    coordinates_sample = np.column_stack((x_sample, y_sample))
    coordinates = np.unique(coordinates_sample, axis=0)
    for i in np.arange(np.size(coordinates,0)):
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        # creating events
        # x
        events['x'].append(coordinates[i][0])
        # y
        events['y'].append(coordinates[i][1])
        # ts
        events['ts'].append(ts)
        # pol
        events['pol'].append(pol)
        # idx
        events['idx'].append(coordinates[i][0] * height + coordinates[i][1])
        frame[coordinates[i][1], coordinates[i][0]] = 1

# Visualization
    plt.ion()
    plt.imshow(frame)
    plt.draw()
    plt.pause(0.1)
    frame = np.zeros((width, height))