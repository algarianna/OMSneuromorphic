import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random

# os.system('cls')
matplotlib.use('TkAgg')

# camera resolution
width = 50
height = 50
v = 142  # px/s  50 - 142 given the max saccade latency at 350 ms and the frame width at 50 px
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

# Creation of the incoherent events
width_inc = 20
height_inc = 20
v_inc = 100  # px/s
t_period_inc = 1 / v_inc
sp_freq = round(width_inc / l)
ind = 0

for x_inc in np.arange(round(width/2 - width_inc/2), round(width/2 + width_inc/2)):
    coord_inc: list = []
    t_inc = ind / v_inc  # starting time-point at each shift but probably useless
    for i in np.arange(sp_freq):
        for y_inc in np.arange(round(height/2 - height_inc/2), round(height/2 + height_inc/2)):
            if width/2 - width_inc/2 < (x_inc + 2 * i * l) < width/2 + width_inc/2:
                coord_inc.append((x_inc + 2 * i * l, y_inc))
            if width/2 - width_inc/2 < ((x_inc + 2 * i * l) - l) < width/2 + width_inc/2:
                coord_inc.append((((x_inc + 2 * i * l) - l), y_inc))
            if width/2 - width_inc/2 < (x_inc - 2 * i * l) < width/2 + width_inc/2:
                coord_inc.append((x_inc - 2 * i * l, y_inc))
            if width/2 - width_inc/2 < ((x_inc - 2 * i * l) - l) < width/2 + width_inc/2:
                coord_inc.append(((x_inc - 2 * i * l) - l, y_inc))

    random.shuffle(coord_inc)
    time_window_inc = np.round(np.linspace(0, t_period_inc, len(coord_inc), endpoint=False), 5)
    for i, (x_pos, y_pos) in enumerate(coord_inc):
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        # creating events
        # x
        events['x'].append(x_pos)
        # y
        events['y'].append(y_pos)
        # ts
        events['ts'].append(t_inc + time_window_inc[i])
        # pol
        events['pol'].append(pol[1])
        # idx
        events['idx'].append(x_pos * height + y_pos)
    ind += sp_freq

np.sort(events['ts'])
np.save("events.npy", events)

# # Visualization
# frame = np.zeros((height, width))
# t_period_state = t_period_inc
# plt.ion()
# fig = plt.figure()
# ax = fig.add_subplot(111)

# for idx in np.arange(len(events['x'])):
#     if events['ts'][idx] < t_period_state:
#         frame[(events['y'][idx], events['x'][idx])] = 1
#     else:
#         ax.matshow(frame)  # or ax.imshow(frame)
#         plt.draw()
#         plt.pause(0.2)
#         t_period_state += t_period_inc
#         frame = np.zeros((height, width))
#         frame[(events['y'][idx], events['x'][idx])] = 1
