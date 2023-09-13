import matplotlib.pyplot as plt
import numpy as np
from brian2 import *
from brian2tools import *
import itertools
import random


# matplotlib.use('TkAgg')


# # Visualizing connectivity
def visualise_syn_connectivity(synapse, pre, post):
    ns = len(synapse.source)
    nt = len(synapse.target)
    figure(figsize=(25, 8))

    plot(zeros(ns), arange(ns), 'ok', ms=10)
    plot(ones(nt), arange(nt), 'ok', ms=10)
    for i, j in zip(synapse.i, synapse.j):
        plot([0, 1], [i, j], '-k')
    xticks([0, 1], [pre, post])
    ylabel('Neuron index')
    xlim(-0.1, 1.1)
    ylim(-1, max(ns, nt))
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
    RF_size = round(width / sqrt(N_neurons))  # row length / number of RF in one row

    # Create a grid of zeros
    RF = np.zeros((width, width))

    # Create a coordinate grid
    x = np.arange(width)
    y = np.arange(width)
    xx, yy = np.meshgrid(x, y)

    # Neurons arrangement
    neurons = [np.int_(np.sqrt(N_neurons)), np.int_(np.sqrt(N_neurons))]

    # Generate the circle mask
    radius = RF_size // 2  # Radius of the circle
    # pitch = (RF_size - neurons[0] * radius * 2) / (neurons[0] + 1)
    # circles_size = [radius * 2 * neurons[0] + RF_size // 4 * (neurons[0] - 1),
    #                 radius * 2 * neurons[1] + pitch * (neurons[1] - 1)]

    centers_x = np.linspace(width / neurons[0] / 2, width - radius - (width / neurons[0] / 2), neurons[0],
                            endpoint='true')
    centers_y = np.linspace(width / neurons[0] / 2, width - radius - (width / neurons[0] / 2), neurons[1],
                            endpoint='true')

    centers = [(x, y) for x in centers_x for y in centers_y]

    # np.array((centers_x, centers_y)).T

    spikes = []
    for i in np.arange(len(spike_times)):
        for j in np.arange(len(spike_times[i])):
            spikes.append((spike_times[i][j], i))
    spikes.sort()

    i = 0
    # for t in np.arange(0.0 * second, sim_time, 0.5 * ms):
    #     print(t)
    #     if i < len(spikes):
    #         if t > spikes[i][0]
    return spikes, centers, xx, yy, radius


def plot_mean_firing_rate(spike_train, bin_size):
    """
    Plots the mean firing rate of a neuron given a spike train.

    Parameters:
        spike_train (numpy array): Array containing the spike times of the neuron.
        bin_size (float): Size of the time bins in which spikes will be counted (in seconds).
    """
    # Calculate the number of bins
    num_bins = int(np.ceil(spike_train[-1] / bin_size))

    # Create an array to hold the spike counts in each bin
    spike_counts = np.zeros(num_bins)

    # Iterate over each spike and increment the corresponding bin
    for spike in spike_train:
        bin_index = int(spike / bin_size)
        spike_counts[bin_index] += 1

    # Calculate the mean firing rate in each bin
    mean_firing_rate = spike_counts / bin_size

    # Create an array of time points for the x-axis of the plot
    time_points = np.arange(num_bins) * bin_size

    # Plot the mean firing rate
    plt.plot(time_points, mean_firing_rate)
    plt.xlabel('Time (s)')
    plt.ylabel('Mean Firing Rate (Hz)')
    plt.title('Mean Firing Rate of Neuron')
    plt.show()


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
    width = 60
    height = 60
    N = width * height
    coordinates = [(x, y) for x in range(width) for y in range(height)]
    time = 1  # second    last event time
    # t_period = round(time / len(coordinates), 4)   # second
    # t_period = 1/8 * second
    # events = create_events(coordinates, height, time)
    events = np.load("events.npy", allow_pickle='TRUE').item()
    # visualisation(height, width, events, t_period)

    DVS = SpikeGeneratorGroup(N, events['idx'], events['ts'] * second, dt=10 * usecond)
    eqs = '''
    dv/dt = (I-v)/tau : 1  
    I : 1
    tau : second
    '''

    RF_per_row = 3
    RF_size: int = width // RF_per_row  # RFs pixel size is RF_size x RF_size
    RF_N = N // (RF_size ** 2)  # number of RFs
    RF_perc = 0.75
    RF_active = round(RF_size ** 2 * RF_perc)
    RF_thr = 0.2
    # Adding a threshold and the reset to 0 after a spike. (to add RP : refractory  = 3*ms)
    RF = NeuronGroup(RF_N, eqs, threshold='v>RF_thr', reset='v=0', method='exact')
    RF.tau = 10 * ms

    # Down sampling from DVS to RF
    indexes = []  # pre synaptic neuron indexes
    for a in np.arange(0, height * (height - RF_size) + 1, RF_size * height):  # Calculating the starting index for
        # each sample column
        for b in np.arange(a, a + height - RF_size + 1, RF_size):  # Calculating the starting index for
            # each sample row
            for c in np.arange(RF_size):  # Going over RF width
                for cc in np.arange(RF_size):  # Going over RF height
                    indexes.append(b + c * height + cc)  # All indexes in each sample
    indexes = np.array(indexes)
    indexes = np.resize(indexes, (RF_N, RF_size ** 2))

    S_DVS_RF = Synapses(DVS, RF, on_pre='v_post +=1')

    for rf in np.arange(RF_N):
        S_DVS_RF.connect(i=indexes[rf], j=rf)

    # visualise_syn_connectivity(S_DVS_RF, 'DVS', 'RF')

    # Amacrine cell to suppress coherent stimuli
    A_thr = 6
    A = NeuronGroup(1, eqs, threshold='v>A_thr', method='exact')  # refractory=3*ms
    A.tau = 5 * ms

    # Synapse between RF cells and Amacrine
    RF_to_A = Synapses(RF, A, on_pre='v_post +=0.02')
    RF_to_A.connect()
    visualise_syn_connectivity(RF_to_A, RF, A)

    OMS_thr = 2
    OMS = NeuronGroup(1, eqs, threshold='v>OMS_thr', reset='v=0', method='exact')  # refractory=3*ms
    OMS.tau = 100 * ms

    RF_to_OMS = Synapses(RF, OMS, on_pre='v_post +=1')
    RF_to_OMS.connect(i=4, j=0)
    RF_to_OMS.delay = 150 * ms
    visualise_syn_connectivity(RF_to_OMS, RF, OMS)

    # Synapse between Amacrine and OMS cell
    A_to_OMS = Synapses(A, OMS, on_pre='v_post +=-1.5')
    A_to_OMS.connect()

    DVS_spike_mon = SpikeMonitor(DVS)

    RF_spike_mon = SpikeMonitor(RF)
    RF_state_mon = StateMonitor(RF, 'v', record=True)  # Recording state variable v during a run
    RF_rate = PopulationRateMonitor(RF)
    # RF_rate_smoothed = PopulationRateMonitor.smooth_rate(RF_rate,window="gaussian", width=0.02*second)

    A_spike_mon = SpikeMonitor(A)  # Recording spikes
    A_state_mon = StateMonitor(A, 'v', record=True)  # Recording state variable v during a run
    A_fr_mon = PopulationRateMonitor(A)

    OMS_spike_mon = SpikeMonitor(OMS)  # Recording spikes
    OMS_state_mon = StateMonitor(OMS, 'v', record=True)  # Recording state variable v during a run
    OMS_fr_mon = PopulationRateMonitor(OMS)

    sim_time = 400 * ms
    run(sim_time)
    figure()
    brian_plot(DVS_spike_mon)
    brian_plot(RF_spike_mon)
    brian_plot(A_spike_mon)
    brian_plot(OMS_spike_mon)

    # for i in np.arange(RF_N):
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

    DVS_spike_times = DVS_spike_mon.spike_trains()

    # DVS spikes visualization
    # dvs, ax = plt.subplots(width, height)
    # dvs.suptitle("DVS Spikes")
    # for idx in np.arange(width):
    #     for idy in np.arange(height):
    #         ax[idx, idy].vlines(DVS_spikes[idx + idy * height], 0, 1)
    #         ax[idx, idy].set_xticks([])
    #         ax[idx, idy].set_yticks([])
    #         ax[idx, idy].set_xlim(0, sim_time / second)
    #         # ax[idx, idy].axis('off')
    # dvs.show()

    # figure()
    # plt.plot(DVS_spike_mon.i, DVS_spike_mon.t / ms, '.')
    # ylim(0, 2500)
    # xlim(0, sim_time)

    A_spike_times = A_spike_mon.spike_trains()
    RF_spike_times = RF_spike_mon.spike_trains()
    # plot(RF_rate_smoothed.t / ms, RF_rate_smoothed.rate / Hz)

    # RF spikes visualization
    # rf, ax = plt.subplots(RF_per_row, RF_per_row)
    # rf.suptitle('RF Spikes')
    # for idx in np.arange(RF_per_row):
    #     for idy in np.arange(RF_per_row):
    #         ax[idx, idy].vlines(RF_spike_times[idx + idy * RF_per_row], 0, 1)
    #         ax[idx, idy].set_xticks([])
    #         ax[idx, idy].set_yticks([])
    #         ax[idx, idy].set_xlim(0, sim_time / second)
    #         # ax[idx, idy].axis('off')
    # rf.show()

    # RF_spikes, RF_centers, xx, yy, radius = view_spikes(width, RF_spike_times)
    #
    OMS_spike_times = OMS_spike_mon.spike_trains()
    # OMS_spikes, OMS_centers, xx, yy, radius = view_spikes(width, OMS_spike_times)

    # dvs, ax = plt.subplots(9, 1, figsize=(10, 25))
    # dvs.suptitle('DVS Spikes')
    # for id in np.arange(9):
    #     ax[id].vlines(DVS_spike_times[id], 0, 1)
    #     ax[id].set_xticks([])
    #     ax[id].set_yticks([])
    #     ax[id].set_xlim(0, sim_time / second)
    #     # ax[idx, idy].axis('off')
    # dvs.show()

    # Population spikes visualization
    rasterplot, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1, figsize=(10, 25))

    ax1.vlines(DVS_spike_times[0], 0, 1)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_xlim(0, sim_time / second)
    ax1.set_ylabel('DVS background')

    ax2.vlines(DVS_spike_times[80], 0, 1)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_xlim(0, sim_time / second)
    ax2.set_ylabel('DVS object')


    ax3.vlines(RF_spike_times[0], 0, 1)
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.set_xlim(0, sim_time / second)
    ax3.set_ylabel('RF background')


    ax4.vlines(RF_spike_times[4], 0, 1)
    ax4.set_xticks([])
    ax4.set_yticks([])
    ax4.set_xlim(0, sim_time / second)
    ax4.set_ylabel('RF object')


    ax5.vlines(A_spike_times[0], 0, 1)
    ax5.set_xticks([])
    ax5.set_yticks([])
    ax5.set_xlim(0, sim_time / second)
    ax5.set_ylabel('Amacrine')


    ax6.vlines(OMS_spike_times[0], 0, 1)
    ax6.set_xlim(0, sim_time / second)
    ax6.set_yticks([])
    ax6.set_ylabel('OMS')
    ax6.set_xlabel('Time (s)')

    rasterplot.show()

    # rf, ax = plt.subplots(RF_per_row, RF_per_row, figsize=(10, 25))
    # rf.suptitle('RF Spikes')
    # for id in np.arange(6)
    #         ax[id].vlines(RF_spike_times[idx + idy * RF_per_row], 0, 1)
    #         ax[id.set_xticks([])
    #         ax[idx, idy].set_yticks([])
    #         ax[idx, idy].set_xlim(0, sim_time / second)
    #         # ax[idx, idy].axis('off')
    # rf.show()

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
    #     if idx < max(events['idx']):
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

    amacrines, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(25, 10))
    amacrines.suptitle('Grating incoherent object region')
    # RF 1 cell voltage plot
    RF_cell = 0
    ax1.plot(RF_state_mon.t / ms, RF_state_mon.v[RF_cell], 'r')
    ax1.set_xlabel('Time [ms]')
    ax1.set_ylabel('Voltage')
    ax1.set_ylim(top=10)
    ax1.set_title('Input cell #' + str(RF_cell) + ' voltage')
    ax1.axhline(RF_thr, ls='--', c='C2', lw=2)

    # RF 1 cell FR plot
    RF_cell = 4
    ax2.plot(RF_state_mon.t / ms, RF_state_mon.v[RF_cell], 'r')
    # ax2.set_xlabel('Time [ms]')
    # ax2.set_ylabel('Voltage')
    ax2.set_ylim(top=10)
    ax2.set_title('Input cell #' + str(RF_cell) + ' voltage')
    ax2.axhline(RF_thr, ls='--', c='C2', lw=2)

    # Amacrine voltage plot
    ax3.plot(A_state_mon.t / ms, A_state_mon.v[0], 'r')
    # ax3.set_xlabel('Time [ms]')
    # ax3.set_ylabel('Voltage ')
    ax3.set_ylim(top=10)
    ax3.set_title('Amacrine cell voltage')
    ax3.axhline(A_thr, ls='--', c='C2', lw=2)

    # OMS cell voltage plot
    ax4.plot(OMS_state_mon.t / ms, OMS_state_mon.v[0], 'r')
    # ax4.set_xlabel('Time [ms]')
    # ax4.set_ylabel('Voltage ')
    ax4.set_ylim(top=10)
    ax4.set_title('OMS cell voltage')

    amacrines.show()
    # ax7.plot(A_s_fr_mon.t / ms, A_s_fr_mon.rate / Hz)
    # ax7.set_xlabel('Time [ms]')
    # # ax7.set_ylabel('Firing rate [Hz] ')
    # ax7.set_title('Amacrine (slow) firing rate')
    #
    # ax8.plot(A_m_fr_mon.t / ms, A_m_fr_mon.rate / Hz)
    # ax8.set_xlabel('Time [ms]')
    # # ax8.set_ylabel('Firing rate [Hz] ')
    # ax8.set_title('Amacrine (medium) firing rate')

    # ax9.plot(A_f_fr_mon.t / ms, A_f_fr_mon.rate / Hz)
    # ax9.set_xlabel('Time [ms]')
    # # ax9.set_ylabel('Firing rate [Hz] ')
    # ax9.set_title('Amacrine (fast) firing rate')

    # for i in arange(RF_N):
    #     cell = 0
    #     ax5.plot(OMS_state_mon.t / ms, OMS_state_mon.v[cell], 'r')
    #     # ax5.set_xlabel('Time [ms]')
    #     # ax5.set_ylabel('Voltage ')
    #     ax5.set_ylim(-6, +6)
    #     ax5.set_title('Output cell #'+str(cell)+'  voltage')
    #     ax5.axhline(OMS_thr, ls='--', c='C2', lw=2)
    #
    #     ax10.plot(OMS_fr_mon.t / ms, OMS_fr_mon.rate / Hz)
    #     ax10.set_xlabel('Time [ms]')
    #     # ax10.set_ylabel('Firing rate [Hz] ')
    #     ax10.set_title('OMS cell #' + str(cell) + ' firing rate')

    plt.show()
