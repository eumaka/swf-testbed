#!/bin/bash
set -e

# Print a single 100-character line of '*' between two blank lines as the first output
printf "\n%100s\n\n" | tr ' ' '*'

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Use PARENT_DIR if set by install.sh, otherwise exit with error
if [[ -z "$PARENT_DIR" ]]; then
    echo "❌ Error: PARENT_DIR not set"
    echo "   Please run install.sh from swf-testbed directory first"
    exit 1
fi

# Autodiscover all swf-* repos in the parent directory
REPOS=()
while IFS= read -r -d '' dir; do
    REPOS+=("$(basename "$dir")")
done < <(find "$PARENT_DIR" -maxdepth 1 -type d -name 'swf-*' -print0 | sort -z)

for repo in "${REPOS[@]}"; do
    REPO_PATH="$PARENT_DIR/$repo"
    TEST_SCRIPT="$REPO_PATH/run_tests.sh"
    echo "--- Running tests for $repo ---"
    if [ -x "$TEST_SCRIPT" ]; then
        # Prevent recursion: do not run run_all_tests.sh from within itself
        if [ "$repo" == "swf-testbed" ] && [ "$SCRIPT_DIR" == "$REPO_PATH" ]; then
            echo "[SKIP] Skipping recursive call to run_all_tests.sh in $repo."
        else
            (cd "$REPO_PATH" && ./run_tests.sh)
        fi
    else
        echo "[SKIP] No test runner found for $repo. Skipping."
    fi
    echo "--- Finished $repo ---"
done

echo "--- All tests completed successfully ---"
