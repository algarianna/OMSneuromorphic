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
v = 10  # px/s
t_period = 0.1  # s
l = 5

# white bar on dark background
pol = [1, 0]
# dark bar on white background
pol = [0, 1]
idx = 0
y_array = np.arange(height)
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
for x in np.arange(width):
    np.random.shuffle(y_array)
    for y in y_array:
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        t = x / v  # s
        # creating events
        # x
        events['x'].append(x)
        # y
        events['y'].append(y)
        # ts
        events['ts'].append(t)
        # pol
        events['pol'].append(pol[1])
        # idx
        events['idx'].append(x * height + y)
        if l < x < (width - l):
            # x
            events['x'].append(x - l)
            # y
            events['y'].append(y)
            # ts
            events['ts'].append(t)
            # pol
            events['pol'].append(pol[1])
            # idx
            events['idx'].append((x - l) * height + y)

# outfile = TemporaryFile()
np.save("events.npy", events)
# events_np = np.load("events.npy", allow_pickle='TRUE').item()
# print(events_np)
# Visualization
frame = np.zeros((height, width))
t_period_state = t_period
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)

for idx in np.arange(len(events['x'])):
    if events['ts'][idx] < t_period_state:
        frame[(events['y'][idx], events['x'][idx])] = 1
    else:
        ax.matshow(frame)  # or ax.imshow(frame)
        plt.draw()
        plt.pause(0.01)
        t_period_state += t_period
        frame = np.zeros((height, width))
        frame[(events['y'][idx], events['x'][idx])] = 1