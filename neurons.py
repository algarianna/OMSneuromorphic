import matplotlib.pyplot as plt
import numpy as np
from brian2 import *
from brian2tools import *
import random

matplotlib.use('TkAgg')


# # Visualizing connectivity
def visualise_syn_connectivity(synapse, pre, post):
    Ns = len(synapse.source)
    Nt = len(synapse.target)
    figure(figsize=(25, 8))

    plot(zeros(Ns), arange(Ns), 'ok', ms=10)
    plot(ones(Nt), arange(Nt), 'ok', ms=10)
    for i, j in zip(synapse.i, synapse.j):
        plot([0, 1], [i, j], '-k')
    xticks([0, 1], [pre, post])
    ylabel('Neuron index')
    xlim(-0.1, 1.1)
    ylim(-1, max(Ns, Nt))
    plt.show()


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


def view_spikes(width, spike_times):
    # Set the dimensions of the frame
    N_neurons = len(spike_times)  # N_neurons = number of RFs in the visual field. Each RF is composed of n pixels
    RF_size = round(width/sqrt(N_neurons))  # row length / number of RF in one row


    # Create a grid of zeros
    RF = np.zeros((width, width))

    # Create a coordinate grid
    x = np.arange(width)
    y = np.arange(width)
    xx, yy = np.meshgrid(x, y)

    # Neurons arrangement
    neurons = [round(sqrt(N_neurons)), round(sqrt(N_neurons))]

    # Generate the circle mask
    radius = RF_size // 2  # Radius of the circle
    # pitch = (RF_size - neurons[0] * radius * 2) / (neurons[0] + 1)
    # circles_size = [radius * 2 * neurons[0] + RF_size // 4 * (neurons[0] - 1),
    #                 radius * 2 * neurons[1] + pitch * (neurons[1] - 1)]

    centers_x = np.linspace(width/neurons[0]/2, width - radius - (width/neurons[0]/2), neurons[0], endpoint = 'true')
    centers_y = np.linspace(width/neurons[0]/2, width - radius - (width/neurons[0]/2), neurons[1], endpoint = 'true')

    centers = []
    for x in centers_x:
        for y in centers_y:
            centers.append((x, y))

    spikes = []
    for i in arange(len(spike_times)):
        for j in arange(len(spike_times[i])):
            spikes.append((spike_times[i][j], i))
    spikes.sort()

    i = 0
    # for t in np.arange(0.0 * second, sim_time, 0.5 * ms):
    #     print(t)
    #     if i < len(spikes):
    #         if t > spikes[i][0]
    return spikes, centers, xx, yy, radius

def mindiff(arr, n):
    # Sort array in non-decreasing order
    arr = sorted(arr)
    # Initialize difference as infinite
    diff = 10 ** 20
    # Find the min diff by comparing adjacent
    # pairs in sorted array
    for i in range(n - 1):
        if arr[i + 1] - arr[i] < diff:
            diff = arr[i + 1] - arr[i]
    # Return min diff
    return diff

if __name__ == "__main__":
    width = 50
    height = 50
    N = width * height
    coordinates = [(x, y) for x in range(width) for y in range(height)]
    time = 1  # second    last event time
    # t_period = round(time / len(coordinates), 4)   # second
    # t_period = 1/8 * second
    # events = create_events(coordinates, height, time)
    events = np.load("events.npy", allow_pickle='TRUE').item()
    # visualisation(height, width, events, t_period)

    DVS = SpikeGeneratorGroup(N, events['idx'], events['ts'] * second, dt=10*usecond)
    eqs = '''
    dv/dt = (I-v)/tau : 1  
    I : 1
    tau : second
    '''
    RF_size: int = width//5  # RFs pixel size is 2x2
    RF_N = N // (RF_size ** 2)  # number of RFs
    RF_perc = 0.75
    RF_active = round(RF_size ** 2 * RF_perc)
    RF_thr = 5
    # Adding a threshold and the reset to 0 after a spike. (to add RP : refractory  = 3*ms)
    RF = NeuronGroup(RF_N, eqs, threshold='v>RF_thr', reset='v=0', method='exact')
    RF.tau = 100 * ms
    S_DVS_RF = Synapses(DVS, RF, on_pre='v_post +=1')

    # Down sampling from DVS to RF
    idx = []  # pre synaptic neuron indexes
    for a in np.arange(0, height * (height - RF_size) + 1, RF_size * height):
        for b in np.arange(a, a + height - RF_size + 1, RF_size):
            for c in np.arange(RF_size):
                for cc in np.arange(RF_size):
                    idx.append(b + c * height + cc)
    idx = np.array(idx)
    idx = np.resize(idx, (RF_N, RF_size**2))
    print(idx)
    for c in np.arange(RF_N):
        S_DVS_RF.connect(i=idx[c], j=c)

    # visualise_syn_connectivity(S_DVS_RF, 'DVS', 'RF')

    A_thr = 6
    A = NeuronGroup(1, eqs, threshold='v>A_thr', method='exact')  # refractory=3*ms
    A.tau = 100 * ms

    RF_to_A = Synapses(RF, A, on_pre='v_post +=0.02')
    RF_to_A.connect()

    OMS_thr = 2
    OMS = NeuronGroup(RF_N, eqs, threshold='v>OMS_thr', reset='v=0', method='exact')  # refractory=3*ms
    OMS.tau = 100 * ms

    RF_to_OMS = Synapses(RF, OMS, on_pre='v_post +=1')
    RF_to_OMS.connect('i==j')
    RF_to_OMS.delay = 100*ms

    A_to_OMS = Synapses(A, OMS, on_pre='v_post +=-1')
    A_to_OMS.connect()

    DVS_spike_mon = SpikeMonitor(DVS)

    RF_spike_mon = SpikeMonitor(RF)
    RF_state_mon = StateMonitor(RF, 'v', record=True)  # Recording state variable v during a run

    A_spike_mon = SpikeMonitor(A)  # Recording spikes
    A_state_mon = StateMonitor(A, 'v', record=True)  # Recording state variable v during a run

    OMS_spike_mon = SpikeMonitor(OMS)  # Recording spikes
    OMS_state_mon = StateMonitor(OMS, 'v', record=True)  # Recording state variable v during a run

    sim_time = 400 * ms
    run(sim_time)
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

    RF_spike_times = RF_spike_mon.spike_trains()
    RF_spikes, RF_centers, xx, yy, radius = view_spikes(width, RF_spike_times)

    OMS_spike_times = OMS_spike_mon.spike_trains()
    OMS_spikes, OMS_centers, xx, yy, radius = view_spikes(width, OMS_spike_times)

    # frame = np.zeros((height, width))
    # RF_frame = np.zeros((width, width))
    # OMS_frame = np.zeros((width, width))
    # t_period = 1 / 142 * second
    # t_period_state = t_period
    # plt.ion()
    # fig, ax = plt.subplots(1, 3)
    # plt.title("Coherent motion")
    #
    # idx = 0
    # idxx = 0
    # idxxx = 0
    # for t in np.arange(0.0, sim_time, 5e-03*second):
    #     if idx < len(events['ts']):
    #         while (events['ts'][idx] * second) < t:
    #             frame[(events['y'][idx], events['x'][idx])] = 1
    #             idx+=1
    #
    #     if idxx < len(RF_spikes):
    #         while RF_spikes[idxx][0] < t:
    #             circle_mask = ((xx - RF_centers[(RF_spikes[idxx][1])][0]) ** 2 + (yy - RF_centers[(RF_spikes[idxx][1])][1]) ** 2) <= radius ** 2
    #             RF_frame[circle_mask] = 1  # Set the values inside the circle to ones
    #             idxx += 1
    #
    #     if idxxx < len(OMS_spikes):
    #         while OMS_spikes[idxxx][0] < t:
    #             circle_mask = ((xx - OMS_centers[(OMS_spikes[idxxx][1])][0]) ** 2 + (yy - OMS_centers[(OMS_spikes[idxxx][1])][1]) ** 2) <= radius ** 2
    #             OMS_frame[circle_mask] = 1  # Set the values inside the circle to ones
    #             idxxx += 1
    #
    #     ax[0].matshow(frame)  # or ax.imshow(frame)
    #     ax[0].set_title('Events')
    #     ax[1].matshow(RF_frame)
    #     ax[1].set_title('Input layer')
    #     ax[2].matshow(OMS_frame)
    #     ax[2].set_title('Output layer')
    #     plt.draw()
    #     plt.pause(0.0001)
    #
    #     frame = np.zeros((height, width))
    #     # frame[(events['y'][idx], events['x'][idx])] = 1
    #     RF_frame = np.zeros((width, width))
    #     OMS_frame = np.zeros((width, width))

    figure()
    RF_cell = 0
    plt.plot(RF_state_mon.t / ms, RF_state_mon.v[RF_cell], 'r')
    xlabel('Time [ms]')
    ylabel('Voltage ')
    # ylim(top=10)
    title('Input cell #' + str(RF_cell) +' voltage')
    axhline(RF_thr, ls='--', c='C2', lw=2)
    plt.show()

    figure()
    plt.plot(A_state_mon.t/ms, A_state_mon.v[0], 'r')
    xlabel('Time [ms]')
    ylabel('Voltage ')
    ylim(top=10)
    title('Amacrine cell voltage')
    axhline(A_thr, ls='--', c='C2', lw=2)
    plt.show()

    figure()
# for i in arange(RF_N):
    cell = 0
    plt.plot(OMS_state_mon.t / ms, OMS_state_mon.v[cell], 'r')
    xlabel('Time [ms]')
    ylabel('Voltage ')
    ylim(-6, +6)
    title('Output cell #'+str(cell)+'  voltage')
    axhline(OMS_thr, ls='--', c='C2', lw=2)
    plt.show()
    k = 0


