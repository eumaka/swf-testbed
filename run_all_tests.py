#!/usr/bin/env python3
"""Run tests across all swf-* repositories."""
import os
import sys
import subprocess
from pathlib import Path

def print_separator():
    """Print the 100-character separator line."""
    print("\n" + "*" * 100 + "\n")

def activate_venv():
    """Activate virtual environment if needed."""
    venv_path = Path(__file__).parent / ".venv"
    if "VIRTUAL_ENV" not in os.environ and venv_path.exists():
        print("🔧 Auto-activating virtual environment...")
        # For subprocess calls, we need to use the venv's Python
        venv_python = venv_path / "bin" / "python"
        if venv_python.exists():
            os.environ["VIRTUAL_ENV"] = str(venv_path)
            os.environ["PATH"] = f"{venv_path}/bin:{os.environ['PATH']}"
            # Update sys.executable to point to venv Python
            sys.executable = str(venv_python)
    else:
        # Use system Python3 if no venv available
        if not venv_path.exists():
            print("🔧 No virtual environment found, using system Python3...")
            sys.executable = "/usr/bin/python3"

def find_swf_repos(parent_dir):
    """Find all swf-* repositories in parent directory."""
    repos = []
    for item in sorted(Path(parent_dir).iterdir()):
        if item.is_dir() and item.name.startswith("swf-"):
            repos.append(item)
    return repos

def run_tests_for_repo(repo_path):
    """Run tests for a single repository."""
    repo_name = repo_path.name
    print(f"--- Running tests for {repo_name} ---")
    
    test_script = repo_path / "run_tests.py"
    
    if test_script.exists() and os.access(test_script, os.X_OK):
        # For swf-testbed, avoid recursion by running the Python script directly
        if repo_name == "swf-testbed" and repo_path == Path(__file__).parent:
            print("Running swf-testbed tests (preventing recursion)...")
            # Import and run the test script's main function directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("run_tests", test_script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.main() == 0
        else:
            # Run the repository's Python test script with our environment
            env = os.environ.copy()
            env["SWF_PARENT_DIR"] = str(repo_path.parent)
            result = subprocess.run([sys.executable, str(test_script)], cwd=repo_path, env=env)
            return result.returncode == 0
    else:
        print(f"[SKIP] No run_tests.py found for {repo_name}. Skipping.")
        return True

def main():
    """Main function."""
    print_separator()
    
    # Get directories
    script_dir = Path(__file__).resolve().parent
    swf_parent_dir = script_dir.parent
    
    # Activate virtual environment
    activate_venv()
    
    # Find and run tests for all repos
    repos = find_swf_repos(swf_parent_dir)
    print(f"Found {len(repos)} swf-* repositories in {swf_parent_dir}")
    
    all_passed = True
    
    for repo in repos:
        success = run_tests_for_repo(repo)
        if not success:
            all_passed = False
        print(f"--- Finished {repo.name} ---")
    
    if all_passed:
        print("--- All tests completed successfully ---")
        return 0
    else:
        print("--- Some tests failed ---")
        return 1

if __name__ == "__main__":
    sys.exit(main())