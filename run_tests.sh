#!/usr/bin/env bash
set -e

# Print a single 100-character line of '*' between two blank lines as the first output
printf "\n%100s\n\n" | tr ' ' '*'

# This script runs all tests for the swf-testbed project using the unified
# virtual environment. It detects which repos are present, runs their tests,
# and summarizes results. Exits nonzero if any repo's tests fail.

# Activate the project environment. This sets SWF_HOME and activates the venv.
source "$(dirname "${BASH_SOURCE[0]}")/setup_env.sh"

# Report environment info ONCE at the top
if [ -z "$ENV_INFO_PRINTED" ]; then
    echo "SWF Testbed Unified Test Runner"
    echo "SWF_HOME: $SWF_HOME"
    echo "Python executable: $(which python)"
    echo "Python version: $(python --version)"
    echo "Virtualenv: $VIRTUAL_ENV"
    export ENV_INFO_PRINTED=1
fi

# Dynamically discover all swf-* repo directories in SWF_HOME
REPOS=()
while IFS= read -r -d '' dir; do
    REPOS+=("$(basename "$dir")")
done < <(find "$SWF_HOME" -maxdepth 1 -type d -name 'swf-*' -print0 | sort -z)

ANY_FAIL=0

for repo in "${REPOS[@]}"; do
    REPO_PATH="$SWF_HOME/$repo"
    TEST_SCRIPT="$REPO_PATH/run_tests.sh"
    echo
    echo "----- $repo -----"
    if [ ! -d "$REPO_PATH" ]; then
        echo "[SKIP] Repo directory $REPO_PATH not found. Skipping."
        continue
    fi
    if [ -x "$TEST_SCRIPT" ] && [ "$repo" != "swf-testbed" ]; then
        (cd "$REPO_PATH" && ./run_tests.sh --no-header)
        STATUS=$?
    elif [ "$repo" == "swf-testbed" ]; then
        if [ -d "$REPO_PATH/tests" ]; then
            (cd "$REPO_PATH" && python -m pytest tests)
            STATUS=$?
        else
            echo "[SKIP] No tests/ directory found in $repo. Skipping."
            continue
        fi
    else
        echo "[SKIP] No test script found in $repo. Skipping."
        continue
    fi
    if [ $STATUS -eq 0 ]; then
        echo "[PASS] $repo tests passed."
    else
        echo "[FAIL] $repo tests failed!"
        ANY_FAIL=1
    fi
    echo

done

echo
if [ $ANY_FAIL -eq 0 ]; then
    echo "=== ALL TEST SUITES PASSED ==="
    exit 0
else
    echo "=== SOME TEST SUITES FAILED ==="
    exit 1
fi
