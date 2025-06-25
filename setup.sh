#!/usr/bin/env bash

# This script sets up the unified Python virtual environment for the entire
# swf-testbed project. It installs all necessary dependencies from all
# sub-projects found in the workspace.

set -e  # Exit immediately if a command exits with a non-zero status.

# The root directory of the swf-testbed project, where this script is located.
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PATH="$PROJECT_ROOT/venv"

echo "Creating unified virtual environment at $VENV_PATH..."
python3 -m venv "$VENV_PATH"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

echo "Installing base dependencies..."
python -m pip install --upgrade pip
python -m pip install "wheel" "setuptools" "pytest"

# --- Install dependencies for each sub-project in the correct order ---

# swf-common-lib (must be first as others depend on it)
COMMON_LIB_PATH="$PROJECT_ROOT/../swf-common-lib"
if [ -d "$COMMON_LIB_PATH" ]; then
    if [ -f "$COMMON_LIB_PATH/pyproject.toml" ]; then
        echo "Installing dependencies for swf-common-lib..."
        python -m pip install -e "$COMMON_LIB_PATH"
    fi
else
    echo "swf-common-lib not found, skipping."
fi

# swf-monitor
MONITOR_PATH="$PROJECT_ROOT/../swf-monitor"
if [ -d "$MONITOR_PATH" ]; then
    if [ -f "$MONITOR_PATH/pyproject.toml" ]; then
        echo "Installing dependencies for swf-monitor..."
        python -m pip install -e "$MONITOR_PATH"
    fi
else
    echo "swf-monitor not found, skipping."
fi

# swf-testbed (this project, installed last)
if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    echo "Installing dependencies for swf-testbed..."
    python -m pip install -e "$PROJECT_ROOT"
fi

echo ""
echo "--------------------------------------------------"
echo "Project setup complete."
echo "To activate the environment, run:"
echo "source $VENV_PATH/bin/activate"
echo "--------------------------------------------------"
