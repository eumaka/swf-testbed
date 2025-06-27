"""
This conftest.py ensures that if pytest is run directly on a test file (not via the test script or project root),
it will gently fail with a clear message instructing the user to use the correct test runner for robustness.
"""
import os
import pytest

def pytest_configure(config):
    # For the testbed, we do not expect DJANGO_SETTINGS_MODULE, but we do expect the test script to be used
    if os.path.basename(os.getcwd()) != "swf-testbed":
        pytest.exit(
            "\n[SWF-TESTBED TEST SUITE]\n\n"
            "You are running pytest in a way that does not use the robust test runner.\n"
            "For robust and reliable results, always run tests using:\n"
            "  ./run_tests.sh   (from this repo root)\n"
            "or\n"
            "  ./run_all_tests.sh   (from the umbrella/testbed repo root)\n\n"
            "Direct invocation of pytest on a test file or from the wrong directory is not supported.\n",
            returncode=4
        )
