#!/bin/bash
set -e

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run tests for swf-common-lib
echo "--- Running tests for swf-common-lib ---"
"$SCRIPT_DIR/../swf-common-lib/run_tests.sh"

# Run tests for swf-monitor
echo "--- Running tests for swf-monitor ---"
"$SCRIPT_DIR/../swf-monitor/run_tests.sh"

echo "--- All tests completed successfully ---"
