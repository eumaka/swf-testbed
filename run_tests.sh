#!/bin/bash
set -e

# Print a single 100-character line of '*' between two blank lines as the first output
printf "\n%100s\n\n" | tr ' ' '*'

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"
REQS_TXT="$SCRIPT_DIR/requirements.txt"
PYPROJECT="$SCRIPT_DIR/pyproject.toml"

# If a virtual environment is already active, use it
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Using already active Python environment: $VIRTUAL_ENV"
# Otherwise, try to activate the local venv if it exists
elif [ -d "$VENV_DIR" ]; then
    echo "Activating Python environment from $VENV_DIR"
    source "$VENV_DIR/bin/activate"
# If no environment is active and no venv exists, create a new venv
else
    echo "No active Python environment found. Creating venv at $VENV_DIR."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    # Install dependencies if requirements.txt or pyproject.toml is present
    if [ -f "$REQS_TXT" ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r "$REQS_TXT"
    elif [ -f "$PYPROJECT" ]; then
        echo "Installing dependencies from pyproject.toml..."
        pip install .[test]
    else
        echo "No requirements.txt or pyproject.toml found. Skipping dependency install."
    fi
fi

# Run tests if the tests directory exists and is not empty
if [ -d "$SCRIPT_DIR/tests" ] && [ "$(ls -A "$SCRIPT_DIR/tests" 2>/dev/null)" ]; then
    echo "Running pytest for swf-testbed..."
    pytest tests
else
    echo "[SKIP] No tests/ directory found in swf-testbed. Skipping."
fi
