# Gemini Guidance

This file provides critical operational guidance for the Gemini agent working within the SWF testbed ecosystem.

## **CRITICAL: Command Execution in the Virtual Environment**

**1. Virtual Environment Directory:**
The virtual environment for this project is named `.venv` (a hidden directory), not `venv`. Always use this correct path.

**2. Execution Method:**
To ensure commands run reliably, you **MUST** use the full, absolute path to the python executable within the `.venv` directory. This is the most robust method and avoids issues with shell environment persistence.

   - **Python Executable Path:** `/Users/wenaus/github/swf-testbed/.venv/bin/python3`

First, ensure all dependencies are installed by running the `install.sh` script once.
```bash
# Run this once to set up or update dependencies
cd /Users/wenaus/github/swf-testbed && source ./install.sh
```

### Correct Procedure for Subsequent Commands:

Directly execute commands using the venv's python.

**Example: Running a Django migration in `swf-monitor`**
```bash
/Users/wenaus/github/swf-testbed/.venv/bin/python3 /Users/wenaus/github/swf-monitor/src/manage.py migrate
```

**Example: Running the Django development server**
```bash
/Users/wenaus/github/swf-testbed/.venv/bin/python3 /Users/wenaus/github/swf-monitor/src/manage.py runserver 8001 &
```
