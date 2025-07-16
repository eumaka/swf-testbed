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

---

## **CRITICAL: Checklist for Renaming Components**

Renaming components has far-reaching side effects. A simple rename requires a systematic, multi-step check to ensure the application remains stable. The following checklist is based on recent failures and must be followed for any renaming task.

**Example Scenario:** Renaming a view from `old_name` to `new_name`.

1.  **Rename the View Function:**
    *   In `views.py`, change `def old_name(request):` to `def new_name(request):`.

2.  **Update URL Configuration (`urls.py`):**
    *   **Update Import:** Change `from .views import old_name` to `from .views import new_name`.
    *   **Update `path()`:** Change `path('...', old_name, ...)` to `path('...', new_name, ...)`.
    *   **Update URL Name:** Change `name='old_name'` to `name='new_name'`. This is critical for template tags.
    *   **Check URL Parameters:** Ensure any captured URL parameters (e.g., `<str:table_name>`) match the arguments in the new view function's signature.

3.  **Update Templates (`*.html`):**
    *   **Find and Replace `{% url %}` tags:** Search all templates for `{% url 'monitor_app:old_name' %}` and replace it with `{% url 'monitor_app:new_name' %}`.
    *   **Rename Template File:** If the view renders a template with a corresponding name (e.g., `old_name.html`), rename the file to `new_name.html`.

4.  **Global Code Search:**
    *   Perform a project-wide search for the string `"old_name"` to find any other references in Python code, JavaScript, or comments.

5.  **Verification:**
    *   **Run `manage.py check`:** This is the most important step. It will catch most `ImportError`, `NameError`, and `NoReverseMatch` issues without needing to run the server.
    *   **Restart and Test:** Only after the check passes, restart the server and manually test the affected pages.