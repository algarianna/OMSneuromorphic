# Code creating random events all over the visual field simulating coherent motion

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random
from tempfile import TemporaryFile

# os.system('cls')
matplotlib.use('TkAgg')

# camera resolution
width = 50
height = 50


t = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7] # s
pol = 1
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
frame = np.zeros((width, height))
plt.figure()
num_e = 2000

for ts in t:
    x_sample = np.random.choice(np.arange(width),  size=num_e)
    y_sample = np.random.choice(np.arange(height), size=num_e)
    for i in np.arange(len(x_sample)):
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        # creating events
        # x
        events['x'].append(x_sample[i])
        # y
        events['y'].append(y_sample[i])
        # ts
        events['ts'].append(ts)
        # pol
        events['pol'].append(pol)
        # idx
        events['idx'].append(x_sample[i] * height + y_sample[i])
        frame[y_sample[i], x_sample[i]] = 1
    # Visualization
    # plt.ion()
    plt.imshow(frame)
    plt.draw()
    plt.pause(0.5)
    frame = np.zeros((width, height))

np.save("events.npy", events)




# for t in np.arange(len(events['x'])):
#     if events['ts'][idx] < t_period:
#         frame[(events['y'][idx], events['x'][idx])] = 1
#     else:
#         ax.matshow(frame)  # or ax.imshow(frame)
#         plt.draw()
#         plt.pause(0.1)
#         frame = np.zeros((height, width))
#         frame[(events['y'][idx], events['x'][idx])] = 1
