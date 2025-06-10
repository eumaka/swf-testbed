# swf-testbed

This is the umbrella repository for the ePIC streaming workflow testbed.

The testbed plan is based on ePIC streaming computing model WG discussions in the streaming computing model meeting[^1], guided by the ePIC streaming computing model report[^2], and the ePIC workflow management system requirements draft[^3].

## Testbed plan

The testbed will prototype the ePIC streaming computing model's workflows and dataflows from Echelon 0 (E0) egress (the DAQ exit buffer)
through the processing that takes place at the two Echelon 1 computing facilities at BNL and JLab.

The testbed scope, timeline and workplan are described in a planning document[^4]. Detailed progress tracking and development discussion is in a progress document[^5].

See the E0-E1 overview slide deck [^6] for more information on the E0-E1 workflow and dataflow.
For a schematic of the system the testbed targets see slide 4 (from the blue DAQ external subnet rightwards).

## Design and implementation

Overall system design and implementation notes:

- The implementation language will be Python 3.
- Testbed modules will be implemented as a set of loosely coupled agents, each with a specific role in the system.
- The agents will communicate via messaging, using ActiveMQ as the message broker.
- The PanDA [^7] distributed workload management system and its ancillary components will be used for workflow orchestration and workload execution.
- The Rucio [^8] distributed data management system will be used for management and distribution of data and associated metadata, in close orchestration with PanDA.
- High quality monitoring and centralized management of system data (metadata, bookkeeping, logs etc.) will be a primary design goal. Monitoring and system data gathering and distribution will be implemented via a web service backed by a relational database, with a REST API for data access and reporting.

### Participants

At present the testbed is a project of the Nuclear and Particle Physics Software (NPPS) group at BNL; collaborators are welcome.

- Torre Wenaus (lead)
- Maxim Potekhin
- Ejiro Umaka
- Michel Villanueva
- Xin Zhao

## Software organization

The streaming workflow (swf prefix) set of repositories make up the software for the ePIC
streaming workflow testbed project, development begun in June 2025.
This swf-testbed repository serves as the umbrella repository for the testbed.
It's the central place for documentation, overall configuration,
and high-level project information.

The repositories mapping to testbed components are:

### swf-monitor

A web service providing system monitoring and comprehensive information about the testbed's state, both via browser-based dashboards and a json based REST API.

This module will manage the databases used by the testbed, and offer a REST API for other agents in the system to report status and retrieve information.

Implementation notes:

### swf-daqsim-agent

This is the information agent designed to simulate the Data Acquisition (DAQ) system and other EIC machine and ePIC detector influences on streaming processing.
This dynamic simulator acts as the primary input and driver of activity within the testbed.

Implementation notes:

- Base it on the [pysim](https://pypi.org/project/pysim/) dynamical system modeler.

### swf-data-agent

This is the central data handling agent within the testbed.
It will listen to the swf-daqsim-agent, manage Rucio subscriptions of run datasets and STF files, create new run datasets, and send messages to the swf-processing-agent for run processing and to the swf-fastmon-agent for new STF availability. It will also have a 'watcher' role to identify and report stalls or anomalies.

### swf-processing-agent

This is the prompt processing agent that configures and submits PanDA processing jobs to execute the streaming workflows of the testbed.

### swf-fastmon-agent

This is the fast monitoring agent designed to consume (fractions of) STF data for quick, near real-time monitoring.
This agent will reside at E1 and perform remote data reads from STF files in the DAQ exit buffer, skimming a fraction of the data of interest for fast monitoring. The agent will be notified of new STF availability by the swf-data-agent.

## Glossary

- STF: super time frame. A contiguous set of ~1000 TFs containing about ~0.6s of ePIC data, corresponding to ~2GB. The STF is the atomic unit of streaming data processing.
- TF: time frame. Atomic unit of ePIC detector readout ~0.6ms in duration.

## References

[^1]: [ePIC streaming computing model meeting page](https://docs.google.com/document/d/1t5vBfgro8Kb6MKc-bz2Y67u3cOCpHK4dfepbJX-nEbE/edit?tab=t.0#heading=h.y3evqgz3sc98)

[^2]: [ePIC streaming computing model report](https://zenodo.org/records/14675920)

[^3]: [ePIC workflow management system requirements draft](https://docs.google.com/document/d/1OmAGzFgZgEP6ntuRkP51kiOqF_0uh_RPjq8wgdTwb2A/edit?tab=t.0#heading=h.g1vlz8vqp7ht)

[^4]: [ePIC streaming workflow testbed planning document](https://docs.google.com/document/d/1mPqMsjHiymkeAB7uih_8TjFIluwM8MENIWZF3EDwNrU/edit?tab=t.0)

[^5]: [ePIC streaming workflow testbed progress document](https://docs.google.com/document/d/1PUoo-W6dCeOKsD4VubYTgSxBHBUb4D5dYfVy1oLYh7E/edit?tab=t.0#heading=h.qovfena71s)

[^6]: [E0-E1 overview slide deck](https://docs.google.com/document/d/1t5vBfgro8Kb6MKc-bz2Y67u3cOCpHK4dfepbJX-nEbE/edit?tab=t.0#heading=h.y3evqgz3sc98)

[^7]: [PanDA: Production and Distributed Analysis System](https://link.springer.com/article/10.1007/s41781-024-00114-3)
  [PanDA documentation](https://panda-wms.readthedocs.io/en/latest/index.html)
  [BNL PanDA startup guide](https://docs.google.com/document/d/1zxtpDb44yNmd3qMW6CS7bXCtqZk-li2gPwIwnBfMNNI/edit?tab=t.0#heading=h.iiqfpuwcgs2k)

[^8]: [Rucio: A Distributed Data Management System](https://link.springer.com/article/10.1007/s41781-019-0026-3)
    [Rucio home](https://rucio.cern.ch/)
