#!/usr/bin/env python3
"""Run tests for swf-testbed repository."""
import os
import sys
import subprocess
from pathlib import Path

def print_separator():
    """Print the 100-character separator line."""
    print("\n" + "*" * 100 + "\n")

def main():
    """Main function."""
    print_separator()
    
    # Get the directory of this script
    script_dir = Path(__file__).resolve().parent
    
    # Check if we're in a virtual environment
    venv_path = script_dir / ".venv"
    if "VIRTUAL_ENV" not in os.environ:
        if venv_path.exists():
            print("🔧 Auto-activating virtual environment...")
            # Use the venv's Python for pytest
            venv_python = venv_path / "bin" / "python"
            if venv_python.exists():
                os.environ["VIRTUAL_ENV"] = str(venv_path)
                os.environ["PATH"] = f"{venv_path}/bin:{os.environ['PATH']}"
                sys.executable = str(venv_python)
        else:
            print("❌ Error: No Python virtual environment found")
            print("   Please ensure .venv exists in the swf-testbed directory")
            print("   You can create it with: python3 -m venv .venv")
            return 1
    
    print(f"Using Python environment: {os.environ.get('VIRTUAL_ENV', 'system')}")
    
    # Check if tests directory exists and has content
    tests_dir = script_dir / "tests"
    if tests_dir.exists() and list(tests_dir.iterdir()):
        print("Running pytest for swf-testbed...")
        
        # Run pytest using regular subprocess
        result = subprocess.run([sys.executable, "-m", "pytest", "tests"], cwd=script_dir)
        return result.returncode
    else:
        print("[SKIP] No tests/ directory found in swf-testbed. Skipping.")
        return 0

if __name__ == "__main__":
    sys.exit(main())