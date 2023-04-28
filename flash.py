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

t = np.arange(0, 0.1, 1)  # s
pol = 1
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
frame = np.zeros((width, height))
plt.figure()
num_e = 2000

for ts in t:
    x_sample = np.random.choice(np.arange(width), size=num_e)
    y_sample = [random.randint(height)]
    for i in np.arange(num_e - 1) + 1:
        y_tmp = random.randint(height)
        if y_tmp in y_sample and x_sample[y_sample.index(y_tmp)] == x_sample[i]:
            i = i-2
        else:
            y_sample.append(y_tmp)

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

np.save("new_events.npy", events)
