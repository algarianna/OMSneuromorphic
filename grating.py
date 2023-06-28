import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random

# os.system('cls')
matplotlib.use('TkAgg')

# camera resolution
width = 50
height = 50
v = 49  # px/s  given the max saccade latency at 350 ms and the frame width at 50 px
t_period = 1 / v  # s
l: int = 5
sp_freq: int = round(width / l)

# dark bar on white background
pol = [0, 1]
idx = 0
y_array = np.arange(height)
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
# 100 events happening within each time period
# v = 10 and l = 5 so t_bar_window = 0.5 s

for x in np.arange(width):
    coord: list = []
    t = x / v  # starting time-point at each shift but probably useless
    for i in np.arange(sp_freq):
        for y in y_array:
            if 0 <= (x + 2 * i * l) < width:
                coord.append((x + 2 * i * l, y))
            if 0 <= ((x + 2 * i * l) - l) < width:
                coord.append((((x + 2 * i * l) - l), y))
            if 0 <= (x - 2 * i * l) < width:
                coord.append((x - 2 * i * l, y))
            if 0 <= ((x - 2 * i * l) - l) < width:
                coord.append(((x - 2 * i * l) - l, y))

    random.shuffle(coord)
    time_window = np.round(np.linspace(0, t_period, len(coord), endpoint=False), 5)
    for i, (x_pos, y_pos) in enumerate(coord):
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        # creating events
        # x
        events['x'].append(x_pos)
        # y
        events['y'].append(y_pos)
        # ts
        events['ts'].append(t + time_window[i])
        # pol
        events['pol'].append(pol[1])
        # idx
        events['idx'].append(x_pos * height + y_pos)

np.save("events.npy", events)

# # Visualization
# frame = np.zeros((height, width))
# t_period_state = t_period
# plt.ion()
# fig = plt.figure()
# ax = fig.add_subplot(111)
#
# for idx in np.arange(len(events['x'])):
#     if events['ts'][idx] < t_period_state:
#         frame[(events['y'][idx], events['x'][idx])] = 1
#     else:
#         ax.matshow(frame)  # or ax.imshow(frame)
#         plt.draw()
#         plt.pause(0.2)
#         t_period_state += t_period
#         frame = np.zeros((height, width))
#         frame[(events['y'][idx], events['x'][idx])] = 1
