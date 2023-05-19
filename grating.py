import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random

# os.system('cls')
matplotlib.use('TkAgg')

# camera resolution
width = 50
height = 50
v = 5  # px/s
t_period = 0.1  # s
l: int = 5

# white bar on dark background
pol = [1, 0]
# dark bar on white background
pol = [0, 1]
idx = 0
y_array = np.arange(height)
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
for x in np.arange(l):
    # np.random.shuffle(y_array)
    for y in y_array:
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        t = x / v  # s
        # creating events
        for i in np.arange(np.floor(width/(2*l)), dtype=int):
            # x
            events['x'].append((x + i*2*l))
            # y
            events['y'].append(y)
            # ts
            events['ts'].append(t)
            # pol
            events['pol'].append(pol[1])
            # idx
            events['idx'].append((x + i*l) * height + y)
            # if l < x + i*2*l < (width - l):
            #     # x
            #     events['x'].append(x + i*2*l - l)
            #     # y
            #     events['y'].append(y)
            #     # ts
            #     events['ts'].append(t)
            #     # pol
            #     events['pol'].append(pol[0])
            #     # idx
            #     events['idx'].append((x + i*2*l - l) * height + y)

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