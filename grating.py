import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random

# os.system('cls')
matplotlib.use('TkAgg')

# camera resolution
width = 50
height = 50
v = 1  # px/s
t_period = 1/v  # s
l: int = 5

# dark bar on white background
pol = [0, 1]
idx = 0
y_array = np.arange(height)
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
N = 5  # n. of bars
# 100 events happening within each time period
# v = 10 and l = 5 so t_bar_window = 0.5 s
for x in np.arange(width):
    coord: list = []
    t = x / v  # starting time-point at each shift but probably useless
    for i in np.arange(N):
        for y in y_array:
            coord.append((x + 2*i*l, y))
        if l < (x + 2*i*l):
            for yy in y_array:
                coord.append((((x + 2*i*l)-l), yy))
    np.random.shuffle(coord)
    time_window = np.round(np.arange(0, (1 / v), ((1 / v) / len(coord))), 3)
    for i in np.arange(len(coord)):
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        # creating events
        # x
        events['x'].append(coord[i][0])
        # y
        events['y'].append(coord[i][1])
        # ts
        events['ts'].append(t + time_window[i])
        # pol
        events['pol'].append(pol[1])
        # idx
        events['idx'].append(coord[i][0] * height + coord[i][1])

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
        plt.pause(0.2)
        t_period_state += t_period
        frame = np.zeros((height, width))
        frame[(events['y'][idx], events['x'][idx])] = 1