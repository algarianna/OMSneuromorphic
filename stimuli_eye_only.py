import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random
import random as rnd

# os.system('cls')
matplotlib.use('TkAgg')

# camera resolution
# n.b. 1 pixel = 9.2 um

width = 640  # pixel = 5900 um
height = 480  # pixel = 4400 um
t_period = 0.015  # s jittering period
bars_frequency = 184  # um
l: int = 20  # 184/9.2 pixel black + white bar width
bw_num: int = round(width / l)  # black + white bar number

# dark bar on white background
pol = [0, 1]
idx = 0
y_array = np.arange(height)
events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}

coord = {"x": [], "y": []}

x_start_positions = np.arange(0, width, l)

# Create an array of 10 successive numbers
successive_numbers = np.arange(l // 2)

# Use broadcasting and np.tile to create the desired array
x_positions = x_start_positions[:, np.newaxis] + successive_numbers

# Flatten the result_array into a single row
x_positions = x_positions.flatten()  # or result_array.ravel()
x_position = x_positions[x_positions < width]

for x in x_positions:
    for y in range(height):
        coord['x'].append(x)
        coord['y'].append(y)

sim_time = 1  # s
time = np.round(np.arange(0, sim_time, t_period), 8)
# time_window = np.round(np.linspace(0, t_period, len(coord), endpoint=False), 8)
#
# time = time[:, np.newaxis] + time_window
# time = time.flatten()
possible_jittering_shift = [-1, 1]

for t in time:
    # Combine 'x' and 'y' lists into a single list of (x, y) pairs
    combined = list(zip(coord['x'], coord['y']))
    # Shuffle the combined list
    random.shuffle(combined)
    # Unzip the shuffled list back into 'x' and 'y'
    jitter = rnd.choice(possible_jittering_shift)
    coord_x = np.array(coord['x'])
    coord_x += jitter
    coord_x[coord_x < 0] += width
    coord_x[coord_x >= width] -= width
    coord['x'] = list(coord_x)
    combined = list(zip(coord['x'], coord['y']))
    for x, y in combined:
        # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
        # creating events
        # x
        # if 0 < x < width:
        events['x'].append(x)
        # y
        events['y'].append(y)
        # ts
        events['ts'].append(t)
        # pol
        events['pol'].append(pol[1])
        # idx
        events['idx'].append(x * height + y)

# for e in np.arange(len(events['x'])):
#     if events['idx'][e] < 0 or events['idx'][e] > (width*height):
#         events['x'].remove(events['x'][e])
#         events['y'].remove(events['y'][e])
#         events['ts'].remove(events['ts'][e])
#         events['idx'].remove(events['idx'][e])

# events = [e for e in events for (e['x'] > 0 and e < width)]
# list_1 = [item for item in list_1 if item[2] >= 5 or item[3] >= 0.3]

np.save("events_eye_only.npy", events)

# # Visualization
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
        plt.pause(0.015)
        t_period_state += t_period
        frame = np.zeros((height, width))
        frame[(events['y'][idx], events['x'][idx])] = 1
