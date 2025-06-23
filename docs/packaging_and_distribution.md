# Packaging and Distribution Strategy

This document outlines the strategy for packaging the `swf-testbed` components to support a simple, one-line installation for end-users.

The primary goal is to allow a user to install the entire testbed and its command-line tools via a single command: `pip install swf-testbed`.

## The Strategy: An Umbrella Package with a Management CLI

The `swf-testbed` repository itself will be the source for an "umbrella" Python package. This package will not contain the agent application code directly. Instead, it will serve two main purposes:

1.  **Dependency Management:** It will declare all the individual `swf` components (e.g., `swf-monitor`, `swf-data-agent`) as its dependencies. When a user installs `swf-testbed`, `pip` will automatically find, download, and install all the component packages.
2.  **Management CLI:** It will provide a user-friendly command-line interface (e.g., a `swf-testbed` command) to help the user initialize and manage the testbed environment after the Python packages are installed.

This approach separates the **distribution of code** (handled by `pip` and PyPI) from the **configuration of a running environment** (handled by our CLI).

## Phase 1: Make Each Component an Installable Package

This is the foundational work. Every repository that contains Python code (`swf-common-lib`, `swf-monitor`, `swf-data-agent`, etc.) must be turned into a proper, installable Python package.

For each component repository, the following steps are required:

1.  **Create a `pyproject.toml` file:** This file is the modern standard for defining a Python project's metadata, build system, and dependencies.
2.  **Define Dependencies:** In each component's `pyproject.toml`, list its specific Python dependencies. For example, `swf-monitor` would list `django`, `daphne`, and `swf-common-lib`.
3.  **Adopt a `src` Layout:** The Python source code should be placed within a `src` directory to prevent common import-related issues.

    ```
    swf-monitor/
    ├── src/
    │   └── swf_monitor/
    │       ├── __init__.py
    │       └── ... (all django app code)
    ├── pyproject.toml
    └── README.md
    ```

## Phase 2: Develop the `swf-testbed` Umbrella Package

The `swf-testbed` repository will contain the code for the umbrella package and the management CLI.

1.  **Create `pyproject.toml` for `swf-testbed`:**
    This file will define the project and declare all other `swf` packages as its dependencies. It will also define the entry point for the command-line script.

    ```toml
    [project]
    name = "swf-testbed"
    version = "0.1.0"
    description = "A meta-package to install and manage the ePIC Streaming Workflow Testbed."
    requires-python = ">=3.9"
    dependencies = [
        # List all components to be installed from PyPI
        "swf-common-lib",
        "swf-monitor",
        "swf-daqsim-agent",
        "swf-data-agent",
        "swf-processing-agent",
        "swf-fastmon-agent",
        "swf-mcp-agent",
        # CLI tool dependencies
        "click",
        "supervisor"
    ]

    [project.scripts]
    # This creates the `swf-testbed` command in the user's PATH
    swf-testbed = "swf_testbed_cli.main:cli"
    ```

2.  **Create the Management CLI:**
    A simple command-line tool (e.g., using `click`) will be created within this repository. It will provide commands for the end-user, such as:
    *   `swf-testbed init`: Creates a local runtime environment, including a default `supervisord.conf` and a `logs` directory.
    *   `swf-testbed start`: Starts the testbed services using `supervisord`.
    *   `swf-testbed stop`: Stops the services.
    *   `swf-testbed status`: Checks the status of the services.

## Phase 3: Publishing to PyPI

To enable the global `pip install swf-testbed` command, all packages must be published to the Python Package Index (PyPI).

1.  **Build Distributions:** For each package, create source and wheel distributions using a tool like `python -m build`.
2.  **Upload to PyPI:** Use a tool like `twine` to upload the package distributions to PyPI. The dependency packages (`swf-common-lib`, `swf-monitor`, etc.) must be published before the main `swf-testbed` umbrella package.

## End-User Experience

Once this infrastructure is in place, the experience for a new user will be streamlined:

1.  **Install:**
    ```bash
    pip install swf-testbed
    ```
2.  **Initialize:**
    ```bash
    mkdir my-testbed-runtime
    cd my-testbed-runtime
    swf-testbed init
    ```
3.  **Manage:**
    ```bash
    swf-testbed start
    ```

This provides a professional and maintainable installation path for the entire testbed.
