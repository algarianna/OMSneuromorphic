import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import random
import random as rnd
import pandas as pd

# os.system('cls')
matplotlib.use('TkAgg')

def coordinates (width, height, l):
    coordinates = {"x": [], "y": []}
    # Defining starting x for each bar
    x_start_positions = np.arange(0, width, l)
    # Create an array of 10 successive numbers
    successive_numbers = np.arange(l // 2)

    # Use broadcasting and np.tile to create the desired array
    x_positions = x_start_positions[:, np.newaxis] + successive_numbers

    # Flatten the result_array into a single row
    x_positions = x_positions.flatten()  # or result_array.ravel()
    # x_positions = x_positions[x_positions < width]

    for x in x_positions:
        for y in np.arange(height):
            coordinates['x'].append(x)
            coordinates['y'].append(y)

    return coordinates

if __name__ == "__main__":

    # SURROUND
    # Camera resolution, coherent portion parameters
    width = 640  # pixel = 5900 um
    height = 480  # pixel = 4400 um
    t_period = 0.015  # s jittering period
    bars_frequency = 184  # um
    bar_width: int = 20  # 184/9.2 pixel black + white bar width
    bw_num: int = round(width / bar_width)

    # CENTER
    diameter = 80  # 800 um
    width_inc = 80
    height_inc = 80

    # dark bar on white background
    pol = [0, 1]
    events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}

    sim_time = 1  # s
    time = np.round(np.arange(0, sim_time, t_period), 8)

    possible_jittering_shift = [-1, 1]

    # surround events coordinates
    coord = coordinates(width, height, bar_width)

    x_inc_coordinates = np.arange(round(width//2 - width_inc//2), round(width//2 + width_inc//2))
    y_inc_coordinates = np.arange(round(height//2 - height_inc//2), round(height//2 + height_inc//2))

    # Combine 'x' and 'y' lists into a single list of (x, y) pairs
    surround = list(zip(coord['x'], coord['y']))

    # creation of surround events
    for t in time:
        # Shuffle the combined list
        random.shuffle(surround)
        # Unzip the shuffled list back into 'x' and 'y'
        jitter = rnd.choice(possible_jittering_shift)
        coord['x'], coord['y'] = zip(*surround)
        coord_x = np.array(coord['x'])
        coord_x += jitter
        coord_x[coord_x < 0] += width
        coord_x[coord_x >= width] -= width
        coord['x'] = list(coord_x)
        surround = list(zip(coord['x'], coord['y']))
        for x, y in surround:
            # events is a list of tuples: (x position, y position, time in seconds, on/off polarity)
            # creating events
            # x
            if not (x in x_inc_coordinates and y in y_inc_coordinates):
                events['x'].append(x)
                # y
                events['y'].append(y)
                # ts
                events['ts'].append(t)
                # pol
                events['pol'].append(pol[1])
                # idx
                events['idx'].append(x * height + y)

    # creation of object coordinates
    coordinates = {"x": [], "y": []}
    # Defining starting x for each bar
    x_start_positions = np.arange(np.round(width//2 - width_inc//2), np.round(width//2 + width_inc//2), bar_width)
    # Create an array of 10 successive numbers
    successive_numbers = np.arange(bar_width // 2)
    # Use broadcasting and np.tile to create the desired array
    x_positions = x_start_positions[:, np.newaxis] + successive_numbers

    # Flatten the result_array into a single row
    x_positions = x_positions.flatten()  # or result_array.ravel()
    # x_positions = x_positions[np.any(np.round(width//2 - width_inc//2) < x_positions < np.round(width//2 + width_inc//2))]

    y_array = np.arange(np.round(height//2 - height_inc//2), np.round(height//2 + height_inc//2))

    for x in x_positions:
        for y in y_array:
            coordinates['x'].append(x)
            coordinates['y'].append(y)

    # creation of center events
    for t in time:
        # Combine 'x' and 'y' lists into a single list of (x, y) pairs
        combined = list(zip(coordinates['x'], coordinates['y']))
        # Shuffle the combined list
        random.shuffle(combined)
        # Unzip the shuffled list back into 'x' and 'y'
        jitter = rnd.choice(possible_jittering_shift)
        coord_x = np.array(coordinates['x'])
        coord_x += jitter
        # for x in coord_x:
        #     if x >= np.round(width // 2 + width_inc // 2):
        #         x_roll = x + width_inc
        #         if x_roll in coord_x:
        #             coord_x = np.delete(coord_x, np.argwhere(coord_x >= np.round(width // 2 + width_inc // 2)))
        #         else:
        #
        #             coord_x = np.delete(coord_x, np.argwhere(coord_x < np.round(width // 2 - width_inc // 2)))
        coord_x[coord_x > np.round(width // 2 - width_inc // 2)] -= width_inc
        coord_x[coord_x < np.round(width//2 - width_inc//2)] += width_inc

        coordinates['x'] = list(coord_x)
        combined = list(zip(coordinates['x'], coordinates['y']))
        successive_timings = np.arange(0, t_period, t_period / (height * bw_num * bar_width))
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

    event_tuples = list(zip(events["x"], events["y"], events["ts"], events["pol"], events["idx"]))

    # Initialize a dictionary to store the indices of each unique combination
    unique_combinations_indices = {}

    # Iterate through the event tuples and store their indices

    for index, event_tuple in enumerate(event_tuples):
        if event_tuple not in unique_combinations_indices:
            unique_combinations_indices[event_tuple] = [index]
        else:
            unique_combinations_indices[event_tuple].append(index)

    # Find and print the duplicate combinations along with their indices
    for event_tuple, indices in unique_combinations_indices.items():
        if len(indices) > 1:
            print(f"Duplicate combination {event_tuple} found at indices: {indices}")

    events = pd.DataFrame(events).sort_values(by='ts').to_dict('list')
    np.sort(events['ts'])
    np.save("events_eye_object.npy", events)

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
