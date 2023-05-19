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
l: int = 5

# white bar on dark background
pol = [1, 0]
# dark bar on white background
pol = [0, 1]
idx = 0
y_array = np.arange(height)
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
# 100 events happening within each time period
# v = 10 and l = 5 so t_bar_window = 0.5 s
for x in np.arange(width):
    np.random.shuffle(y_array)
    if l < x < (width - l):
        time_window = np.arange(0, (1 / v), (0.1 / 2 * height))  # 100 timepoints for 100 events
    else:
        time_window = np.arange(0, (1 / v), (0.1 / height))  # 50 timepoints for 50 events
    np.random.shuffle(time_window)
    t = x / v  # starting time-point at each shift but probably useless
    dt = 0  # index to get time_window timepoints
    for y in y_array:
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        # creating events
        # x
        events['x'].append(x)
        # y
        events['y'].append(y)
        # ts
        events['ts'].append(t + time_window[dt])
        # pol
        events['pol'].append(pol[1])
        # idx
        events['idx'].append(x * height + y)
        dt += 1
        if l < x < (width - l):
            # x
            events['x'].append(x - l)
            # y
            events['y'].append(y)
            # ts
            events['ts'].append(t + time_window[dt])
            # pol
            events['pol'].append(pol[1])
            # idx
            events['idx'].append((x - l) * height + y)
            dt += 1

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
        plt.pause(0.001)
        t_period_state += t_period
        frame = np.zeros((height, width))
        frame[(events['y'][idx], events['x'][idx])] = 1