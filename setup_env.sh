#!/bin/bash
# This script is intended to be sourced to set up the environment for the SWF testbed.
#
# Usage: source setup_env.sh
#
# It determines the location of the swf-testbed directory and sets the SWF_HOME
# environment variable to its parent directory. This allows for a portable setup
# that works regardless of where you have cloned the project.

# Get the absolute path of the directory containing this script (i.e., swf-testbed).
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# Set SWF_HOME to the parent directory of the script's location.
# This is the directory assumed to contain all the swf-* repositories.
export SWF_HOME=$(dirname "$SCRIPT_DIR")

echo "SWF_HOME set to: $SWF_HOME"

# You can add other environment setup tasks here in the future.
# For example:
# export ANOTHER_VAR="some_value"
