# swf-testbed

This is the umbrella repository for the ePIC streaming workflow testbed.

The testbed plan is based on ePIC streaming computing model WG discussions
in the streaming computing model meeting[^1], guided by the ePIC streaming
computing model report[^2], and the ePIC workflow management system
requirements draft[^3].

## Testbed plan

The testbed prototypes the ePIC streaming computing model's workflows and
dataflows from Echelon 0 (E0) egress (the DAQ exit buffer)
through the processing that takes place at the two Echelon 1 computing
facilities at BNL and JLab.

The testbed scope, timeline and workplan are described in a planning
document[^4]. Detailed progress tracking and development discussion is in a
progress document[^5].

See the E0-E1 overview slide deck [^6] for more information on the E0-E1
workflow and dataflow.
The following is a schematic of the system the testbed targets (from the blue
DAQ external subnet rightwards).

![E0-E1 workflow schematic](images/E0-E1_workflow_schematic.png)

*Figure: E0-E1 data flow and processing schematic*

## Design and implementation

Overall system design and implementation notes:

- The implementation language is Python 3.9 or greater.
- Testbed modules are implemented as a set of loosely coupled agents, each
  with a specific role in the system.
- The agents communicate via messaging, using ActiveMQ as the message
  broker.
- The PanDA [^7] distributed workload management system and its ancillary
  components are used for workflow orchestration and workload execution.
- The Rucio [^8] distributed data management system is used for
  management and distribution of data and associated metadata, in close
  orchestration with PanDA.
- High quality monitoring and centralized management of system data (metadata,
  bookkeeping, logs etc.) is a primary design goal. Monitoring and system
  data gathering and distribution is implemented via a web service backed
  by a relational database, with a REST API for data access and reporting.

### Prompt Tips

**Note to the AI Assistant:** The following "Prompt Tips" are a guide for our
collaboration on this project. Please review them carefully and integrate them
into your operational context to ensure your contributions are consistent,
high-quality, and aligned with the project's standards.

#### General

- **Adhere to established standards and conventions.** When implementing new
  features, prioritize the use of established standards, conventions, and
  naming schemes provided by the programming language, frameworks, or
  widely-used libraries. Avoid introducing custom terminology or patterns when a
  standard equivalent exists.
- **Favor Simplicity and Maintainability.** Strive for clean, simple, and
  maintainable solutions. When faced with multiple implementation options,
  recommend the one that is easiest to understand, modify, and debug. Avoid
  overly complex or clever code that might be difficult for others (or your
  future self) to comprehend. Adhere to the principle of "Keep It Simple,
  Stupid" (KISS).
- **Follow Markdown Linting Rules.** Ensure all markdown content adheres to the
  project's linting rules. This includes, but is not limited to, line length,
  list formatting, and spacing. Consistent formatting improves readability and
  maintainability.
- **Maintain the prompts.** Proactively suggest additions or modifications to
  these tips as the project evolves and new collaboration patterns emerge.

#### Project-Specific

- **Context Refresh.** To regain context on the SWF Testbed project, follow
  these steps:
    1. Review the high-level goals and architecture in `swf-testbed/README.md`
       and `swf-testbed/docs/architecture_and_design_choices.md`.
    2. Examine the dependencies and structure by checking the `pyproject.toml`
       and `requirements.txt` files in each sub-project (`swf-testbed`,
       `swf-monitor`, `swf-common-lib`).
    3. Use file and code exploration tools to investigate the existing codebase
       relevant to the current task. For data models, check `models.py`; for
       APIs, check `urls.py` and `views.py`.
    4. Consult the conversation summary to understand recent changes and
       immediate task objectives.

- **Verify and Propose Names.** Before implementing new names for variables,
  functions, classes, context keys, or other identifiers, first check for
  consistency with existing names across the relevant context. Once verified,
  propose them for review. This practice ensures clarity and reduces rework.

### Participants

At present the testbed is a project of the Nuclear and Particle Physics
Software (NPPS) group at BNL; collaborators are welcome.

- Torre Wenaus (lead)
- Maxim Potekhin
- Ejiro Umaka
- Michel Villanueva
- Xin Zhao

## Testbed Infrastructure

### Environment Setup

To prepare your environment for running the testbed, simply `source` the
provided setup script:

```bash
source setup.sh
```

This script automatically determines the project's root directory (assuming all
`swf-*` repositories are siblings) and sets the `SWF_HOME` environment
variable. This variable is then used by other parts of the testbed, like the
Supervisor configuration, to locate necessary files and directories.

It is recommended to run this command every time you open a new terminal to work
on the project. You can also add it to your shell's startup file (e.g.,
`~/.bash_profile`, `~/.zshrc`) for convenience.

## Running the Testbed

You can run the testbed in two modes: using Docker for managing background
services (PostgreSQL and ActiveMQ), or by running these services locally on
your host machine.

### Using Docker (Recommended)

This is the recommended approach as it provides a consistent, cross-platform
environment.

**Prerequisites:**

- Docker Desktop installed and running.

**Usage:**

The `swf-testbed` CLI provides commands to manage the entire testbed, including
the Docker containers and the Python agents managed by Supervisor.

- `swf-testbed start`: Starts the Docker containers (PostgreSQL, ActiveMQ) and
  then starts all Python agents.
- `swf-testbed stop`: Stops and removes the Docker containers, and stops all
  Python agents.
- `swf-testbed status`: Shows the status of the Docker containers and the
  Python agents.

### Running Locally (Without Docker)

This mode is for users who prefer to manage the background services directly on
their host machine.

**Prerequisites:**

You are responsible for installing and running PostgreSQL and ActiveMQ.

- **PostgreSQL:**
  - **macOS (using Homebrew):**

    ```bash
    brew install postgresql
    brew services start postgresql
    # Optional: Create a user and database
    # createuser -s admin
    # createdb -O admin swfdb
    ```

  - **Other Systems:** Follow the official installation guide for your
    operating system.

- **ActiveMQ:**
  - **macOS (using Homebrew):**

    ```bash
    brew install activemq
    brew services start activemq
    ```

  - **Other Systems:** Download and follow the installation instructions from the
    [ActiveMQ website](https://activemq.apache.org/components/classic/download/).

**Usage:**

The `swf-testbed` CLI also provides commands for managing the testbed services
when they are running locally.

- `swf-testbed start-local`: Starts the Python agents using Supervisor. It
  assumes PostgreSQL and ActiveMQ are already running.
- `swf-testbed stop-local`: Stops the Python agents managed by Supervisor.
- `swf-testbed status-local`: Checks the status of local services (PostgreSQL,
  ActiveMQ) and the Python agents managed by Supervisor.

## Development

### Process Management

We use `supervisor` to manage the various Python agent processes. The
configuration is located in `supervisord.conf`. This file is a template and
should be copied to the root of the project during initialization.

The `swf-testbed init` command will create the `logs` directory and copy the
`supervisord.conf` file for you.

The `supervisord.conf` file is configured to use the `SWF_HOME` environment
variable to locate the various `swf-*` repositories. Make sure you have sourced
the `setup.sh` script before running any `supervisor` commands.

STF availability. It also has a 'watcher' role to identify and report
stalls or anomalies.

Interactions with Rucio are consolidated in this agent.

### [swf-processing-agent](https://github.com/BNLNPPS/swf-processing-agent)

This is the prompt processing agent that configures and submits PanDA
processing jobs to execute the streaming workflows of the testbed.

Interactions with PanDA are consolidated in this agent.

### [swf-fastmon-agent](https://github.com/BNLNPPS/swf-fastmon-agent)

This is the fast monitoring agent designed to consume (fractions of) STF data
for quick, near real-time monitoring. This agent resides at E1 and performs
remote data reads from STF files in the DAQ exit buffer, skimming a fraction
of the data of interest for fast monitoring. The agent is notified of new
STF availability by the swf-data-agent.

### [swf-mcp-agent](https://github.com/BNLNPPS/swf-mcp-agent)

This agent may be added in the future for managing Model Context Protocol
(MCP) services. For the moment, this is done in swf-monitor (Colocated with
the agent data the MCP services provide)


Note Paul Nilsson's [ask-panda
example](https://github.com/PalNilsson/ask-panda) of
  MCP server and client.

## System infrastructure

This repository hosts overall system infrastructure for the testbed software,
including the following.

### Agent process management

The testbed agents are managed by a process manager, which is
responsible for configuring, starting, stopping, and monitoring the agents.

The python [supervisor](http://supervisord.org/) process manager is used.

### Message Broker

The [ActiveMQ](https://activemq.apache.org/) message broker provides the
messaging backbone for the testbed agents to communicate.

#### Local Development Broker

For local development and testing, a standalone broker can be run using Docker.
This is managed by the `docker-compose.yml` file in this repository. To start
the local broker, run:

```bash
docker-compose up -d
```

When using the local broker, the agents should be configured with the following
environment variables:

```bash
export ACTIVEMQ_HOST=localhost
export ACTIVEMQ_PORT=61616
export ACTIVEMQ_USER=admin
export ACTIVEMQ_PASSWORD=admin
```

#### Production Broker

In a production environment, the agents should be configured to use the centrally
provided ActiveMQ service. This is done by setting the same environment variables
 to point to the production broker's host, port, and credentials.

Each agent (e.g., `swf-monitor`, `swf-data-agent`) will need to be configured
to read these environment variables and use them to connect to the broker. The
`swf-monitor` application, for example, reads these values from its Django
`settings.py` file, which in turn can be populated from environment variables.

## Testing

The testbed provides a unified, robust test runner to ensure all components are
tested consistently and automatically.

- To run all tests across all `swf-*` repositories, simply execute:

  ```bash
  ./run_all_tests.sh
  ```

  This script autodiscovers sibling `swf-*` repositories, runs their test
  suites, and reports results with clear separators.

- To run tests for a specific repository, use its own `run_tests.sh` script
  (if present), e.g.:

  ```bash
  ./run_tests.sh
  ```

  in the desired repo directory.

- The test infrastructure is designed to automatically use the active Python
  environment or a local venv if present. If neither is available, the test
  runner will exit with a clear error message.

Test results are printed to the console. For more details, consult the logs or
output of individual test runs.

## Glossary

- STF: super time frame. A contiguous set of ~1000 TFs containing about ~0.6s
  of ePIC data, corresponding to ~2GB. The STF is the atomic unit of
  streaming data processing.
- TF: time frame. Atomic unit of ePIC detector readout ~0.6ms in duration.

## References

[^1]: [ePIC streaming computing model meeting page](https://docs.google.com/document/d/1t5vBfgro8Kb6MKc-bz2Y67u3cOCpHK4dfepbJX-nEbE/edit?tab=t.0#heading=h.y3evqgz3sc98)

[^2]: [ePIC streaming computing model report](https://zenodo.org/records/14675920)

[^3]: [ePIC workflow management system requirements draft](https://docs.google.com/document/d/1OmAGzFgZgEP6ntuRkP51kiOqF_0uh_RPjq8wgdTwb2A/edit?tab=t.0#heading=h.g1vlz8vqp7ht)

[^4]: [ePIC streaming workflow testbed planning document](https://docs.google.com/document/d/1mPqMsjHiymkeAB7uih_8TjFIluwM8MENIWZF3EDwNrU/edit?tab=t.0)

[^5]: [ePIC streaming workflow testbed progress document](https://docs.google.com/document/d/1PUoo-W6dCeOKsD4VubYTgSxBHBUb4D5dYfVy1oLYh7E/edit?tab=t.0#heading=h.qovfena71s)

[^6]: [E0-E1 overview slide deck](https://docs.google.com/presentation/d/1Vbt68LwBDA-eDghlWWg8278ys_K0axbX/edit?slide=id.g2fdc8697d63_0_18#slide=id.g2fdc8697d63_0_18)

[^7]: [PanDA: Production and Distributed Analysis System](https://link.springer.com/article/10.1007/s41781-024-00114-3)
  [PanDA documentation](https://panda-wms.readthedocs.io/en/latest/index.html)
  [BNL PanDA startup guide](https://docs.google.com/document/d/1zxtpDb44yNmd3qMW6CS7bXCtqZk-li2gPwIwnBfMNNI/edit?tab=t.0#heading=h.iiqfpuwcgs2k)

[^8]: [Rucio: A Distributed Data Management System](https://link.springer.com/article/10.1007/s41781-019-0026-3)
    [Rucio home](https://rucio.cern.ch/)
