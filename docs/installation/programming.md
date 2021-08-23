# Programming SpiNNaker

<a href="https://www.frontiersin.org/articles/10.3389/fnins.2018.00816/full"><img src="https://www.frontiersin.org/files/Articles/422311/fnins-12-00816-HTML/image_m/fnins-12-00816-g002.jpg" alt="sPyNNaker workflow" width="600"></a>

<iframe
    width="720"
    height="500"
    src="http://spinnakermanchester.github.io/2015.005.Arbitrary/workshop_material/proceedings/slides/Running_PyNN_Simulations_On_SpiNNaker.pdf#page=4"
    frameborder="0"
    allowfullscreen
></iframe>

**N.B.**: $$runtime[s] = sim\\_time \times time\\_scale\\_factor \times 0.001 [s]$$

## Example: E-I balanced random network

The following pyNN code simulates a balanced E-I random network producing ~15Hz oscillations. It is modified from the [original article](https://www.frontiersin.org/articles/10.3389/fnins.2018.00816/full#supplementary-material) to also run with the NEST backend (minor modifications). The following diagram depicts the simulated E-I network on the left and its allocation on SpiNNaker on the right.

<a href="https://www.frontiersin.org/articles/10.3389/fnins.2018.00816/full"><img src="https://www.frontiersin.org/files/Articles/422311/fnins-12-00816-HTML/image_m/fnins-12-00816-g003.jpg" alt="sPyNNaker workflow" width="750"></a>


```python
import matplotlib.pyplot as plt
from pyNN.utility.plotting import Figure, Panel

# Select pyNN backend: True (SpiNNaker) | False (NEST)
SPINN=True

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
```

The following logs are expected and describe the parsing and allocation steps required to run the simulation on SpiNNaker.

```console
2021-07-14 16:33:22 INFO: Starting execution process
2021-07-14 16:33:22 INFO: Simulating for 5000 1.0ms timesteps using a hardware timestep of 2000us
2021-07-14 16:33:22 INFO: Creating transceiver for 192.168.240.1
2021-07-14 16:33:22 INFO: Working out if machine is booted
2021-07-14 16:33:26 INFO: Attempting to boot machine
2021-07-14 16:33:32 INFO: Found board with version [Version: SC&MP 3.4.1 at SpiNNaker:0:0:0 (built Thu Feb 11 09:36:44 2021)]
2021-07-14 16:33:32 INFO: Machine communication successful
2021-07-14 16:33:32 INFO: Detected a machine on IP address 192.168.240.1 which has 855 cores and 120.0 links
2021-07-14 16:33:32 INFO: Time 0:00:09.984078 taken by MachineGenerator
Preallocating resources for Extra Monitor support vertices
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.166603 taken by PreAllocateResourcesForExtraMonitorSupport
2021-07-14 16:33:33 INFO: Time 0:00:00.000924 taken by NetworkSpecificationReport
Allocating virtual identifiers
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.052791 taken by MallocBasedChipIDAllocator
Writing the board chip report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.010438 taken by BoardChipReport
Adding Splitter selectors where appropriate
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.011010 taken by SpynnakerSplitterSelector
Adding delay extensions as required
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.017571 taken by DelaySupportAdder
Partitioning graph vertices
|0%                          50%                         100%|
    ============================================================
Partitioning graph edges
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.048827 taken by SpYNNakerSplitterPartitioner
Inserting extra monitors into graphs
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.056711 taken by InsertExtraMonitorVerticesToGraphs
Generating partitioner report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.042963 taken by PartitionerReport
Getting number of keys required by each edge using application graph
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.049616 taken by EdgeToNKeysMapper
2021-07-14 16:33:33 INFO: The time scale factor could be reduced to 0.9984375
2021-07-14 16:33:33 INFO: Time 0:00:00.001665 taken by LocalTDMABuilder
Placing graph vertices via spreading over an entire machine
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.027323 taken by SpreaderPlacer
Inserting edges between vertices which require FR speed up functionality.
|0%                          50%                         100%|
    ==============================2021-07-14 16:33:33 INFO: Time 0:00:00.044123 taken by InsertEdgesToExtraMonitorFunctionality
Generating routing tables for data in system processes
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.013708 taken by SystemMulticastRoutingGenerator
Generating fixed router routes
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.009462 taken by FixedRouteRouter
Generating placement report
|0%                          50%                         100%|
    ============================================================
Generating placement by core report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.122088 taken by PlacerReportWithApplicationGraph
Routing
|0%                          50%                         100%|
    ============================================================

2021-07-14 16:33:33 INFO: Time 0:00:00.067651 taken by NerRouteTrafficAware
Discovering tags
|0%                          50%                         100%|
    ============================================================
Allocating tags
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.069058 taken by BasicTagAllocator
Reporting Tags
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.011370 taken by TagReport
Getting constraints for machine graph
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.046024 taken by ProcessPartitionConstraints
Calculating zones
|0%                          50%                         100%|
    ============================================================
Allocating routing keys
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.026348 taken by ZonedRoutingInfoAllocator
Generating Routing info report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.011686 taken by routingInfoReports
Generating routing tables
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.048697 taken by BasicRoutingTableGenerator
2021-07-14 16:33:33 INFO: Time 0:00:00.000709 taken by RouterCollisionPotentialReport
Finding executable start types
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:33 INFO: Time 0:00:00.054683 taken by LocateExecutableStartType
Initialising buffers
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:34 INFO: Time 0:00:00.061239 taken by BufferManagerCreator
Allocating SDRAM for SDRAM outgoing egde partitions
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:34 INFO: Time 0:00:00.050081 taken by SDRAMOutgoingPartitionAllocator
Generating data specifications
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:34 INFO: Time 0:00:00.345865 taken by SpynnakerDataSpecificationWriter
Preparing Routing Tables
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:34 INFO: Time 0:00:00.028915 taken by RoutingSetup
Finding binaries
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:34 INFO: Time 0:00:00.056594 taken by GraphBinaryGatherer
Running pair routing table compression on chip
|0%                          50%                         100%|
    ============================================================

2021-07-14 16:33:38 INFO: Time 0:00:03.463529 taken by PairOnChipRouterCompression
Generating Router table report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:38 INFO: Time 0:00:00.072211 taken by unCompressedRoutingTableReports
loading fixed routes
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:38 INFO: Time 0:00:00.160281 taken by LoadFixedRoutes
Executing data specifications and loading data for system vertices
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:38 INFO: Time 0:00:00.345118 taken by HostExecuteSystemDataSpecification
Loading system executables onto the machine
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:44 INFO: Time 0:00:05.812218 taken by LoadSystemExecutableImages
2021-07-14 16:33:44 INFO: Time 0:00:00.007824 taken by TagsFromMachineReport
Clearing tags
|0%                          50%                         100%|
    ============================================================
Loading Tags
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:44 INFO: Time 0:00:00.130235 taken by TagsLoader
Executing data specifications and loading data for application vertices
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:44 INFO: Time 0:00:00.245682 taken by HostExecuteApplicationDataSpecification
Preparing to Expand Synapses
|0%                          50%                         100%|
    ============================================================
Expanding Synapses
|0%                          50%                         100%|
    ============================================================


2021-07-14 16:33:49 INFO: Time 0:00:04.196806 taken by SynapseExpander
Running bitfield generation on chip
|0%                          50%                         100%|
    ============================================================


2021-07-14 16:33:52 INFO: Time 0:00:03.381924 taken by OnChipBitFieldGenerator
Finalising Retrieved Connections
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:52 INFO: Time 0:00:00.176666 taken by FinishConnectionHolders
Reading Routing Tables from Machine
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:52 INFO: Time 0:00:00.096534 taken by ReadRoutingTablesFromMachine
Generating compressed router table report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:52 INFO: Time 0:00:00.016523 taken by compressedRoutingTableReports
Generating comparison of router table report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:52 INFO: Time 0:00:00.009959 taken by comparisonOfRoutingTablesReport
Generating Routing summary report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:52 INFO: Time 0:00:00.047387 taken by CompressedRouterSummaryReport
Reading Routing Tables from Machine
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:52 INFO: Time 0:00:00.012677 taken by RoutingTableFromMachineReport
Writing fixed route report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:33:52 INFO: Time 0:00:00.073745 taken by FixedRouteFromMachineReport
Loading executables onto the machine
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:03 INFO: Time 0:00:10.234641 taken by LoadApplicationExecutableImages
2021-07-14 16:34:03 INFO: Running for 1 steps for a total of 5000.0ms
2021-07-14 16:34:03 INFO: Run 1 of 1
Generating SDRAM usage report
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:03 INFO: Time 0:00:00.198174 taken by SdramUsageReportPerChip
2021-07-14 16:34:03 INFO: Time 0:00:00.112088 taken by DatabaseInterface
2021-07-14 16:34:03 INFO: ** Notifying external sources that the database is ready for reading **
2021-07-14 16:34:03 INFO: Time 0:00:00.001272 taken by CreateNotificationProtocol
Getting provenance data from machine graph
|0%                          50%                         100%|
    ============================================================
Getting provenance data from application graph
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:03 INFO: Time 0:00:00.136145 taken by GraphProvenanceGatherer
Waiting for cores to be either in PAUSED or READY state
|0%                          50%                         100%|
    ============================================================
Updating run time
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:03 INFO: Time 0:00:00.049472 taken by ChipRuntimeUpdater
2021-07-14 16:34:03 INFO: *** Running simulation... *** 
Loading buffers
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:03 INFO: ** Awaiting for a response from an external source to state its ready for the simulation to start **
2021-07-14 16:34:03 INFO: ** Sending start / resume message to external sources to state the simulation has started or resumed. **
2021-07-14 16:34:03 INFO: ** Awaiting for a response from an external source to state its ready for the simulation to start **
2021-07-14 16:34:03 INFO: Application started; waiting 10.1s for it to stop
2021-07-14 16:34:14 INFO: ** Sending pause / stop message to external sources to state the simulation has been paused or stopped. **
2021-07-14 16:34:14 INFO: Time 0:00:10.318797 taken by ApplicationRunner
Extracting IOBUF from the machine
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:14 INFO: Time 0:00:00.129705 taken by ChipIOBufExtractor
clearing IOBUF from the machine
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:14 INFO: Time 0:00:00.056423 taken by ChipIOBufClearer
Extracting buffers from the last run
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:14 INFO: Time 0:00:00.138498 taken by BufferExtractor
2021-07-14 16:34:14 INFO: Time 0:00:00.000202 taken by FinaliseTimingData
Getting provenance data
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:14 INFO: Time 0:00:00.174452 taken by PlacementsProvenanceGatherer
2021-07-14 16:34:14 INFO: Time 0:00:00.002856 taken by RedundantPacketCountReport
Getting Router Provenance
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:14 INFO: Time 0:00:00.100807 taken by RouterProvenanceGatherer
Getting profile data
|0%                          50%                         100%|
    ============================================================
2021-07-14 16:34:14 INFO: Time 0:00:00.053342 taken by ProfileDataGatherer
Getting spikes for excitatory_pop
|0%                          50%                         100%|
    ============================================================
Getting spikes for inhibitory_pop
|0%                          50%                         100%|
    ============================================================
```

**Plotting**
```python
Figure(Panel(exc_data.segments[0].spiketrains, xlabel='Time', ylabel='spikes', xticks=True, yticks=True),
    Panel(inh_data.segments[0].spiketrains, xlabel='Time', ylabel='spikes', xticks=True, yticks=True), size=(20, 8))
plt.show()
```
 
<img src="../../img/example_output.png" alt="Expected output" width="700"/>

