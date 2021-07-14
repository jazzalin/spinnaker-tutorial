# Balance E-I random network producing ~15Hz oscillations
# Modified from https://www.frontiersin.org/articles/10.3389/fnins.2018.00816/full#supplementary-material
#
# Usage: python -W ignore balanced_network.py
# The plotting utility generates warnings due to a hardcoded color setting; the warnings can be ignored

import matplotlib.pyplot as plt
from pyNN.utility.plotting import Figure, Panel

# Select pyNN backend: True (SpiNNaker) | False (NEST)
SPINN=False

if SPINN:
    import pyNN.spiNNaker as sim
else:
    import pyNN.nest as sim    

# Initialise simulator: 1ms timestep by default --> biological real-time
sim.setup(timestep=1)

# Spike input
poisson_spike_source = sim.Population(250, sim.SpikeSourcePoisson(
    rate=50, duration=5000), label='poisson_source')

spike_source_array = sim.Population(250, sim.SpikeSourceArray,
                                    {'spike_times': [1000]},
                                    label='spike_source')

# Neuron Parameters
cell_params_exc = {
    'tau_m': 20.0, 'cm': 1.0, 'v_rest': -65.0, 'v_reset': -65.0,
    'v_thresh': -50.0, 'tau_syn_E': 5.0, 'tau_syn_I': 15.0,
    'tau_refrac': 0.3, 'i_offset': 0}

cell_params_inh = {
    'tau_m': 20.0, 'cm': 1.0, 'v_rest': -65.0, 'v_reset': -65.0,
    'v_thresh': -50.0, 'tau_syn_E': 5.0, 'tau_syn_I': 5.0,
    'tau_refrac': 0.3, 'i_offset': 0}

# Neuronal populations
pop_exc = sim.Population(500, sim.IF_curr_exp(**cell_params_exc),
                         label='excitatory_pop')

pop_inh = sim.Population(125, sim.IF_curr_exp(**cell_params_inh),
                         label='inhibitory_pop')

# Generate random distributions from which to initialise parameters
rng = sim.NumpyRNG(seed=98766987, parallel_safe=True)

# Initialise membrane potentials uniformly between threshold and resting
if SPINN:
    pop_exc.set(v=sim.RandomDistribution('uniform',
                                        [cell_params_exc['v_reset'],
                                        cell_params_exc['v_thresh']],
                                        rng=rng))
else:
    pop_exc.initialize(v=rng.uniform(cell_params_exc['v_reset'], cell_params_exc['v_thresh']))

# Distribution from which to allocate delays
if SPINN:
    delay_distribution = sim.RandomDistribution('uniform', [1, 10], rng=rng)
else:
    delay_distribution = rng.uniform(1.0, 10.0)

# Spike input projections
spike_source_projection = sim.Projection(spike_source_array, pop_exc,
                                         sim.FixedProbabilityConnector(p_connect=0.05),
                                         synapse_type=sim.StaticSynapse(weight=0.1, delay=delay_distribution),
                                         receptor_type='excitatory')

# Poisson source projections
poisson_projection_exc = sim.Projection(poisson_spike_source, pop_exc,
                                        sim.FixedProbabilityConnector(p_connect=0.2),
                                        synapse_type=sim.StaticSynapse(weight=0.06, delay=delay_distribution),
                                        receptor_type='excitatory')

poisson_projection_inh = sim.Projection(poisson_spike_source, pop_inh,
                                        sim.FixedProbabilityConnector(p_connect=0.2),
                                        synapse_type=sim.StaticSynapse(weight=0.03, delay=delay_distribution),
                                        receptor_type='excitatory')

# Recurrent projections
# TODO: try all-to-all connector instead
exc_exc_rec = sim.Projection(pop_exc, pop_exc,
                             sim.FixedProbabilityConnector(p_connect=0.1),
                             synapse_type=sim.StaticSynapse(weight=0.03, delay=delay_distribution),
                             receptor_type='excitatory')

exc_exc_one_to_one_rec = sim.Projection(pop_exc, pop_exc,
                                        sim.OneToOneConnector(),
                                        synapse_type=sim.StaticSynapse(weight=0.03, delay=delay_distribution),
                                        receptor_type='excitatory')

inh_inh_rec = sim.Projection(pop_inh, pop_inh,
                             sim.FixedProbabilityConnector(p_connect=0.1),
                             synapse_type=sim.StaticSynapse(weight=-0.03, delay=delay_distribution),
                             receptor_type='inhibitory')

# Projections between neuronal populations
exc_to_inh = sim.Projection(pop_exc, pop_inh,
                            sim.FixedProbabilityConnector(p_connect=0.2),
                            synapse_type=sim.StaticSynapse(weight=0.06, delay=delay_distribution),
                            receptor_type='excitatory')

inh_to_exc = sim.Projection(pop_inh, pop_exc,
                            sim.FixedProbabilityConnector(p_connect=0.2),
                            synapse_type=sim.StaticSynapse(weight=-0.06, delay=delay_distribution),
                            receptor_type='inhibitory')

# Specify output recording
pop_exc.record('spikes')
pop_inh.record('spikes')

# Run simulation
sim.run(simtime=5000)

# Extract results data
exc_data = pop_exc.get_data('spikes')
inh_data = pop_inh.get_data('spikes')

# Exit simulation
sim.end()

# Plotting
Figure(Panel(exc_data.segments[0].spiketrains, color='red', xlabel='Time', ylabel='spikes', xticks=True, yticks=True),
      Panel(inh_data.segments[0].spiketrains, color='blue', xlabel='Time', ylabel='spikes', xticks=True, yticks=True), size=(20, 8))
plt.show()
