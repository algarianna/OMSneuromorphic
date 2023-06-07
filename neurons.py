import matplotlib.pyplot as plt
import numpy as np
from brian2 import *
from brian2tools import *
import random
matplotlib.use('TkAgg')

#  sto cercando di posizionare le palline nel visual field quindi devo capire quale e' la coordinata del centro dei cerchi

def create_events(coordinates, height, time):
    events = {"x": [], "y": [], "ts": [], "pol": [], "idx": []}
    time_window = np.round(np.linspace(0, time, len(coordinates), endpoint=False), 4)

    for i, coord in enumerate(coordinates):
        events['x'].append(coord[0])
        events['y'].append(coord[1])
        events['ts'].append(time_window[i])
        events['pol'].append(1)
        events['idx'].append(coord[0] * height + coord[1])
    return events


def visualisation(height, width, events, t_period):
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


def view_spikes(spike_times, stim_time, t_period):
    # Set the dimensions of the frame
    RF_size = 64

    # Create a grid of zeros
    RF = np.zeros((RF_size, RF_size))

    # Create a coordinate grid
    x = np.arange(RF_size)
    y = np.arange(RF_size)
    xx, yy = np.meshgrid(x, y)


    # Generate the circle mask
    center = RF_size // 2  # Center coordinates of the frame
    radius = RF_size // 4  # Radius of the circle
    circle_mask = ((xx - center) ** 2 + (yy - center) ** 2) <= radius ** 2

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    i = 0
    for t in np.arange(0.0, stim_time, t_period):
        print(t)
        if i < len(spike_times):
            if t > spike_times[i]:
                RF[circle_mask] = 1  # Set the values inside the circle to ones
                i += 1
        ax.matshow(RF)
        plt.draw()
        plt.pause(0.1)
        RF = np.zeros((RF_size, RF_size))


if __name__ == "__main__":
    width = 8
    height = 8
    N = width * height
    coordinates = [(x, y) for x in range(width) for y in range(height)]
    time = 1 #second    last event time
    t_period = round(time / len(coordinates), 4)

    events = create_events(coordinates, height, time)
    # events = np.load("events.npy", allow_pickle='TRUE').item()
    # visualisation(height, width, events, t_period)


    DVS = SpikeGeneratorGroup(N, events['idx'], events['ts'] * second)

    eqs = '''
    dv/dt = (I-v)/tau : 1  
    I : 1
    tau : second
    '''
    RF_size: int = 2  # RFs pixel size is 2x2
    RF_N = N // (RF_size**2)  # number of RFs
    RF_perc = 0.75
    RF_active = round(RF_size**2 * RF_perc)
    RF_thr = 2
    RF = NeuronGroup(RF_N, eqs, threshold='v>2.0', reset='v=0', method='exact')  # Adding a threshold and the reset to 0 after a spike. (to add RP : refractory = 3*ms)
    RF.tau = [100] * ms

    S_DVS_RF = Synapses(DVS, RF, on_pre='v_post +=1')

    # Downsampling from DVS to RF
    i = []  # presynaptic neuron indexes
    for a in np.arange(0, height * (height - RF_size) + 1, RF_size * height):
        for b in np.arange(a, a + height - RF_size + 1, RF_size):
            i.append(b)
            i.append(b + 1)
            i.append(b + height)
            i.append(b + height + 1)
    i = np.array(i)
    i = np.resize(i, (RF_N, 4))
    print(i)
    for c in np.arange(RF_N):
        S_DVS_RF.connect(i=i[c], j=c)

    DVS_spike_mon = SpikeMonitor(DVS)

    RF_spike_mon = SpikeMonitor(RF)
    RF_state_mon = StateMonitor(RF, 'v', record=True)  # Recording state variable v during a run

    stim_time = 1  # seconds
    run(stim_time * second)
    # for i in np.arange(RF_num):
    #     figure()
    #     plot(RF_state_mon.t / ms, RF_state_mon.v[i], label='RF ' + str(i + 1))
    #     print(max(RF_state_mon.v[i]))
    #     title('RF #' + str(i) + ' - ' + str(len(events['x'])) + ' events')
    #     xlabel('time(ms)')
    #     ylabel('V (mV)')
    #     ylim(top=3.5)
    # for t in RF_spike_mon.t:
    #     axvline(t / ms, ls='--', c='C1', lw=3)
    #     axhline(RF_thr, ls=':', c='C2', lw=3)

    spike_times = []
    for i in RF_N
        spike_times = RF_spike_mon[i].t / second

    np.round(spike_times, 3)
    view_spikes(spike_times, stim_time, t_period)