#!/bin/bash
set -e

# Print a single 100-character line of '*' between two blank lines as the first output
printf "\n%100s\n\n" | tr ' ' '*'

# Get the directory of the script (swf-testbed)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Auto-activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]] && [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    echo "🔧 Auto-activating virtual environment..."
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Set the parent directory containing all swf-* repos
SWF_PARENT_DIR=$(dirname "$SCRIPT_DIR")

# Autodiscover all swf-* repos in the parent directory
REPOS=()
while IFS= read -r -d '' dir; do
    REPOS+=("$(basename "$dir")")
done < <(find "$SWF_PARENT_DIR" -maxdepth 1 -type d -name 'swf-*' -print0 | sort -z)

for repo in "${REPOS[@]}"; do
    REPO_PATH="$SWF_PARENT_DIR/$repo"
    TEST_SCRIPT="$REPO_PATH/run_tests.sh"
    echo "--- Running tests for $repo ---"
    if [ -x "$TEST_SCRIPT" ]; then
        # For swf-testbed, run its own tests but prevent calling run_all_tests.sh recursively
        if [ "$repo" == "swf-testbed" ] && [ "$SCRIPT_DIR" == "$REPO_PATH" ]; then
            echo "Running swf-testbed tests (preventing recursion)..."
            # Run pytest directly instead of run_tests.sh to avoid potential recursion
            if [ -d "$REPO_PATH/tests" ] && [ "$(ls -A "$REPO_PATH/tests" 2>/dev/null)" ]; then
                echo "Using Python environment: $VIRTUAL_ENV"
                echo "Running pytest for swf-testbed..."
                (cd "$REPO_PATH" && pytest tests)
            else
                echo "[SKIP] No tests/ directory found in swf-testbed. Skipping."
            fi
        else
            (cd "$REPO_PATH" && ./run_tests.sh)
        fi
    else
        echo "[SKIP] No test runner found for $repo. Skipping."
    fi
    echo "--- Finished $repo ---"
done

echo "--- All tests completed successfully ---"
