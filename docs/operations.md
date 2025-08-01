# Operations Guide

Running and managing the SWF Testbed services.

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

### Agent Process Management

The testbed agents are managed by a process manager, which is
responsible for configuring, starting, stopping, and monitoring the agents.

We use `supervisor` to manage the various Python agent processes. The
configuration is located in `supervisord.conf`. This file is a template and
should be copied to the root of the project during initialization.

The `swf-testbed init` command will create the `logs` directory and copy the
`supervisord.conf` file for you.

The `supervisord.conf` file is configured to use the `SWF_HOME` environment
variable to locate the various `swf-*` repositories. This is automatically
configured when you run any `swf-testbed` commands.

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