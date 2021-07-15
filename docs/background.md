# Brain inspired computing with SpiNNaker

<img src="https://neuromorphic.kip.uni-heidelberg.de/c/image/m/default/SpiNNakerLogo.png" alt="SpiNNaker logo" width="300"/>

## Why *neuromorphic* computing?
"Don't simulate a brain, build one!"

- Motivation: design and build from the ground (e.g. transistor) up with a **practical** engineered system in mind

- Dedicated hardware places the *brain* in the physical world &#8594; embodied (neuro)science (e.g. robotics)
    - towards hardware/brain-in-the-loop ?

- Huge discrepancy between the efficiency of a biological brain and artificial *brains*
    - Biological brain communication is event-driven &#8594; asynchronous, local computing
    - **Yet**, over the shortest distances,  communication is best described by analog processes (e.g., chemical process underlying synaptic dynamics)
    - von Neumann architecture bottleneck on conventional computers
    - while GPU and HPC are great at handling large data structures "linearly", brain-like communication involves transmitting small data packets (i.e. spikes) to many targets

&#8756; **VLSI philosophy**: combine IC fabrication and system-level architecture to produce truly integrated systems

- Computational neuroscience: neuromorphic hardware becomes a tool to validate hypotheses

<a href="https://robotics.sciencemag.org/content/5/49/eabd1911"><img src="../docs/img/robotics_neuro.png" alt="Image needed" width="600"></a>

> No neuromorphic system attempts to reproduce all of the biological detail, but all adhere to the idea that computation is **highly distributed** across small computing elements analogous in some way to
neurons, connected into networks, with some degree of **flexibility** in the way **connections** are formed. That much is common; the details vary greatly. - [Steve Furber](https://doi.org/10.1088/1741-2560/13/5/051001)

## Early beginnings
**A historical connection**

<a href="http://www.rossashby.info/letters/turing.html"><img src="http://www.rossashby.info/letters/images/wralx018.jpg" alt="Letter" width="600"></a>

- 1948: Alan Turing presents a *connectionist* approach to computing in *Intelligent Machinery* [(Turing, 1948)](https://www.npl.co.uk/getattachment/about-us/History/Famous-faces/Alan-Turing/80916595-Intelligent-Machinery.pdf?lang=en-GB), with his concept of unorganized machine.

<a href="http://www.alanturing.net/turing_archive/pages/Reference%20Articles/connectionism/Turing%27s%20neural%20networks.html"><img src="http://www.alanturing.net/turing_archive/graphics/turingsbtype.gif" alt="Unorganized machine" width="600"></a>

- 1948: Alan Turing works on the [Manchester computers](https://en.wikipedia.org/wiki/Manchester_computers) (Manchester Mark 1)

<a href="https://blog.scienceandindustrymuseum.org.uk/alan-turing-manchester-connection/"><img src="https://blog.scienceandindustrymuseum.org.uk/wp-content/uploads/2019/07/Turing-Ferranti-marketing-image.jpg" alt="Alan Turing Manchester" width="600"></a>

## Fast forward 30 years ...

"*All neuromorphic roads lead to Carver Mead.*" - [Chris Eliasmith](https://youtu.be/nXyowrK4Nvo)

- 1980: [Carver Mead](http://www.lloydwatts.com/carver_MIT_2004.pdf) and Lynn Conway publish *Introduction to VLSI Systems*

<a href="https://ai.eecs.umich.edu/people/conway/Awards/Electronics/ElectAchiev.html"><img src="https://ai.eecs.umich.edu/people/conway/Awards/Electronics/Highlights.jpg" alt="Mead and Conway" width="600"></a>

- 1981: Carver Mead, John Hopfield and Richard Feynman collaborate on the course *Physics of Computation*
    - 1982: Hopfield popularizes a neural network model of memory which we now know as the *Hopfield network*
    - 1983: Feynman teaches "Potentialities and Limitations of Computing Machines" at Caltech, now known as the *Feynman Lectures on Computation* (1996) and eventually looked at quantum computing. and eventually looked at quantum computing.
    - 1986-1991: Mead and his students create the first neural-chip models to mimic touch (1986), hearing (1988) and vision (1991). Any [working system](https://www.nature.com/articles/s41928-020-0448-2.pdf) made it to Mead's book *Analog VLSI and neural systems* (1989)

- 1991: Misha Mahowald creates the first *silicon retina*, precursor to the dynamic vision sensor (DVS) or **event-camera**

- 1990s: Mead and his students popularize the [address-event representation](https://web.stanford.edu/group/brainsinsilicon/documents/methAER.pdf) (AER) protocol for transferring spikes between bio-inspired chips  
(*high-level*: allocating individual wires to each spike source, or neuron, is not feasible as it becomes increasingly more difficult to scale; instead, associate each spike source with a unique address and use a shared bus)

## Meanwhile ...

- 1980s: [Steve Furber](https://www.youtube.com/watch?v=2e06C-yUwlc) is working for Acorn Computers Limited, which eventually became (in part) ARM
- 1990s: Steve Furber joins the University of Manchester, where he works on novel microprocessors and asynchronous computing.
    - While working on associative memory, the Advanced Processor Technologies group recognizes that the architecture they're after resembles that of a neural network
    - The group's expertise lies in digital architectures and processors, not so much in analog circuit design
- 2000s: Given the importance of scalability, Furber et al. revisit AER which has its limitations for large scale, multicore systems. They transform the bus-based protocol into a packet-switched system, with local routing table on each chips.

## Today

[Steve Furber et al.](https://sos-ch-dk-2.exo.io/public-website-production/filer_public/9b/b2/9bb2d52a-5ff3-4f6e-8a5f-b733608f80b9/bernstein_nmc_sept20.pdf), September 2020:

<iframe
    width="720"
    height="500"
    src="https://sos-ch-dk-2.exo.io/public-website-production/filer_public/9b/b2/9bb2d52a-5ff3-4f6e-8a5f-b733608f80b9/bernstein_nmc_sept20.pdf#page=3"
    frameborder="0"
    allowfullscreen
></iframe>

### IBM TrueNorth

Primary use: real-time cognitive applications

Notable features:

- digital
- purely deterministic (i.e. software model is replicated exactly and software emulator may be used to predict performance of hardware)
- simulates leaky integrate-and-fire (LIF) neurons

<a href="https://iopscience.iop.org/article/10.1088/1741-2560/13/5/051001"><img src="https://cfn-live-content-bucket-iop-org.s3.amazonaws.com/journals/1741-2552/13/5/051001/1/jneaa3660f2_hr.jpg?AWSAccessKeyId=AKIAYDKQL6LTV7YY2HIK&Expires=1626829696&Signature=V%2FihgmWG%2FAfjWt1BGNEkJpqO7KA%3D" alt="TrueNorth" width="400"></a>



### Intel Loihi

Primary use: geared toward practical applications

Notable features:

- digital
- based on leaky integrate-and-fire (LIF) neuron
- **Yet** programmable synapse models for on-chip learning (?)
- ships in different shapes and sizes: Kapoho, Nahuku, Pohoiki

<a href="https://www.intel.ca/content/www/ca/en/research/neuromorphic-computing.html"><img src="https://en.wikichip.org/w/images/thumb/5/51/loihi_nahuku_board.png/1200px-loihi_nahuku_board.png" alt="TrueNorth" width="350"></a>

### BrainScaleS (Heidelberg University, HBP)

Primary use: understanding biological systems, specficially long-term learning

Notable features:

- analog
- physical models of neuronal processes (ionic circuits &#8594; electrical circuits) based on the adaptive exponential integrate-and-fire (AdExp) neuron model
- can run in accelerated mode, up to 10 000 times faster than real-time, hence the long-term learning objective

<a href="https://iopscience.iop.org/article/10.1088/1741-2560/13/5/051001"><img src="https://cfn-live-content-bucket-iop-org.s3.amazonaws.com/journals/1741-2552/13/5/051001/1/jneaa3660f6_hr.jpg?AWSAccessKeyId=AKIAYDKQL6LTV7YY2HIK&Expires=1626829696&Signature=oieKgzwZfsnjrZ3v11ldLkt6D4E%3D" alt="BrainScaleS" width="350"></a>

### SpiNNaker (University of Manchester, HBP)

Primary use: modelling biological nervous systems in biological real-time

Notable features:

- digital (ARM968 processors) (nitpicking: not neuromorphic *per se*, but "neurocomputer" or "neural accelerator")
- massively parallel computing
- programmable models (allows researching different neural models and plasticity rules)
- design guidelines: scalability and energy-efficiency

The **efficiency** stems from the highly distributed architecture and the close proximity of processing and memory units (i.e., frequently used data is kept within 1-2 mm of the processor on each core).

<img src="https://www.researchgate.net/publication/325792393/figure/fig2/AS:637841730183181@1529084727458/The-48-node-864-core-SpiNNaker-circuit-board-Online-version-in-colour.png" alt="SpiNNaker chip organization" width="300"><img src="https://apt.cs.manchester.ac.uk/Images/spinn_labeled_bw.png" alt="SpiNNaker chip organization" width="300">

The **scalability** is supported by local routing and the ingenious organization/stacking of boards.

<iframe
    width="720"
    height="500"
    src="https://ec.europa.eu/information_society/newsroom/image/document/2017-8/1_furber_steve_and_meier_karlheinz_CDA4E45F-EF31-6FBF-1642BB9BAB97CEF4_43088.pdf#page=15"
    frameborder="0"
    allowfullscreen
></iframe>

**March, 2016**: \\(18 \times 48 \times 24 \times 5 \times 5 = 518 400\\) core machine

**October, 2018**: \\(18 \times 48 \times 24 \times 5 \times 10 = 1 036 800\\) core machine

<a href="https://en.wikipedia.org/wiki/SpiNNaker"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Spinn_1m_pano.jpg/1024px-Spinn_1m_pano.jpg" alt="1mio core SpiNNaker" width="750"></a>

**2021-2022**: SpiNNaker2

**Further reading**

- [SpiNNaker 2](https://arxiv.org/pdf/1911.02385.pdf) (early stage, 2019)
- [Book about the SpiNNaker project](https://www.research.manchester.ac.uk/portal/files/161744279/978_1_68083_653_0.pdf): *SpiNNaker: A Spiking Neural Network Architecture*, Furber & Bogdan (2020)
- [sPyNNaker: using PyNN on SpiNNaker](https://www.frontiersin.org/articles/10.3389/fnins.2018.00816/full) (2018, version: 4.0.0, **latest: 6.0.0**)
