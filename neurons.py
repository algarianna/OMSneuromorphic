from brian2 import *
%matplotlib inline
matplotlib.use('TkAgg')
events_np = np.load("events.npy", allow_pickle='TRUE').item()
start_scope()
# (unless refractory)
# LIF neuron
eqs = '''
dv/dt = (I-v)/tau : 1  
I : 1
tau : second
'''

# NeuronGroup for creating Bipolar Cells (B)
# Adding a threshold and the reset to 0 after a spike.
N = 25  # 25 neurons are placed on the visual field. Their positions are defined by considering the two diagonals,
# a vertical central line and a horizontal central line. One neuron is positioned at the center of the visual field,
# 8 small-range neurons are positioned at equal distance from the center, each on one of the eight resulting lines
# drawn before, 8 medium-range neurons are positioned further away from the center in the same way and, finally,
# 8 long-range neurons are placed in correspondence of the intersection of the lines and the edge of the visual field.

# The placement of the neurons are to cover the full visual field equally. Therefore, depending on the angle you can
# displace the number of neurons you want on each angle.

indices = array([0, 0, 0])
times = array([1, 2, 3])*ms
B = SpikeGeneratorGroup(1, indices, times)

G = NeuronGroup(3, eqs, threshold='v>1', reset='v=0', method='exact')
feedforward = Synapses(B, G, on_pre='v_post +=0.6')
feedforward.connect(j='i')
recurrent = Synapses(G, G, on_pre='v_post +=0.6')
recurrent.connect('i!=j')
spike_mon = SpikeMonitor(G)
# ...
run(100*ms)


OMS = NeuronGroup(N, eqs, threshold='v>1', reset='v=0', method='exact')  # refractory=3*ms
# Setting the input for the cells.
OMS.I = zeros(N)
OMS.I[0] = 1
# Setting the time constant
OMS.tau = ones(N) * 10 * ms

# NeuronGroup for creating a single Amacrine Cell (A)
A = NeuronGroup(1, eqs, threshold='v>1', reset='v=0', method='exact')  # refractory=3*ms
# Setting the input for the cells.
A.I = 0
# Setting the time constant
A.tau = 10 * ms

# Excitation synapses from BP cells to the A cell
S = Synapses(B, A, on_pre='v_post +=0.6')
S.connect()


# Visualizing connectivity
def visualise_connectivity(S):
    Ns = len(S.source)
    Nt = len(S.target)
    figure(figsize=(25, 8))

    plot(zeros(Ns), arange(Ns), 'ok', ms=10)
    plot(ones(Nt), arange(Nt), 'ok', ms=10)
    for i, j in zip(S.i, S.j):
        plot([0, 1], [i, j], '-k')
    xticks([0, 1], ['OMS', 'A'])
    ylabel('Neuron index')
    xlim(-0.1, 1.1)
    ylim(-1, max(Ns, Nt))


visualise_connectivity(S)

# Inhibitory synapses from A cell to all OMS (G) cells
S = Synapses(A, B, on_pre='v_post -=0.6')
S.connect()


# Visualizing connectivity
def visualise_connectivity(S):
    Ns = len(S.source)
    Nt = len(S.target)
    figure(figsize=(25, 8))

    plot(zeros(Ns), arange(Ns), 'ok', ms=10)
    plot(ones(Nt), arange(Nt), 'ok', ms=10)
    for i, j in zip(S.i, S.j):
        plot([0, 1], [i, j], '-k')
    xticks([0, 1], ['A', 'OMS'])
    ylabel('Neuron index')
    xlim(-0.1, 1.1)
    ylim(-1, max(Ns, Nt))


visualise_connectivity(S)

a = 1