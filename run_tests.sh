#!/usr/bin/env bash
set -e

# This script runs all tests for the swf-testbed project using the unified
# virtual environment.

# Activate the project environment. This sets SWF_HOME and activates the venv.
source "$(dirname "${BASH_SOURCE[0]}")/setup_env.sh"

# --- Run tests for each sub-project ---
# We use SWF_HOME which is set by setup_env.sh

echo "--- Running tests for swf-common-lib ---"
python -m pytest "$SWF_HOME/swf-common-lib"

echo "--- Running tests for swf-monitor ---"
python -m pytest "$SWF_HOME/swf-monitor"

echo "--- Running tests for swf-testbed ---"
python -m pytest "$SWF_HOME/swf-testbed"

echo "--- All tests completed successfully ---"
