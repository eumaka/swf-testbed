#!/bin/bash
set -e

# Print a single 100-character line of '*' between two blank lines as the first output
printf "\n%100s\n\n" | tr ' ' '*'

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Auto-activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]] && [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    echo "🔧 Auto-activating virtual environment..."
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Check if a virtual environment is active after auto-activation attempt
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: No Python virtual environment found"
    echo "   Please ensure .venv exists in the swf-testbed directory"
    echo "   You can create it with: python3 -m venv .venv"
    exit 1
fi

echo "Using Python environment: $VIRTUAL_ENV"

# Run tests if the tests directory exists and is not empty
if [ -d "$SCRIPT_DIR/tests" ] && [ "$(ls -A "$SCRIPT_DIR/tests" 2>/dev/null)" ]; then
    echo "Running pytest for swf-testbed..."
    pytest tests
else
    echo "[SKIP] No tests/ directory found in swf-testbed. Skipping."
fi
