# Packaging and Distribution Strategy

This document outlines the strategy for packaging the `swf-testbed` components
to support a simple, one-line installation for end-users, using a private
Python package index.

The primary goal is to allow a user to install the entire testbed and its
command-line tools via a single command: `pip install swf-testbed`, without
publishing any code publicly.

## The Strategy: An Umbrella Package with a Management CLI

The `swf-testbed` repository itself will be the source for an "umbrella" Python
package. This package will not contain the agent application code directly.
Instead, it will serve two main purposes:

1.  **Dependency Management:** It will declare all the individual `swf`
    components (e.g., `swf-monitor`, `swf-data-agent`) as its dependencies. When
    a user installs `swf-testbed`, `pip` will automatically find, download, and
    install all the component packages from your private package index.
2.  **Management CLI:** It will provide a user-friendly command-line interface
    (e.g., a `swf-testbed` command) to help the user initialize and manage the
    testbed environment after the Python packages are installed.

This approach separates the **distribution of code** (handled by `pip` and a
private package index) from the **configuration of a running environment**
(handled by our CLI).

## Phase 1: Make Each Component an Installable Package

This is the foundational work. Every repository that contains Python code
(`swf-common-lib`, `swf-monitor`, `swf-data-agent`, etc.) must be turned into a
proper, installable Python package.

For each component repository, the following steps are required:

1.  **Create a `pyproject.toml` file:** This file is the modern standard for
    defining a Python project's metadata, build system, and dependencies.
2.  **Define Dependencies:** In each component's `pyproject.toml`, list its
    specific Python dependencies. For example, `swf-monitor` would list `django`,
    `daphne`, and `swf-common-lib`.
3.  **Adopt a `src` Layout:** The Python source code should be placed within a
    `src` directory to prevent common import-related issues.

    ```
    swf-monitor/
    ├── src/
    │   └── swf_monitor/
    │       ├── __init__.py
    │       └── ... (all django app code)
    ├── pyproject.toml
    └── README.md
    ```

## Phase 2: Develop the `swf-testbed` Umbrella Package

The `swf-testbed` repository will contain the code for the umbrella package and
the management CLI.

1.  **Create `pyproject.toml` for `swf-testbed`:**
    This file will define the project and declare all other `swf` packages as
    its dependencies using their simple names.

    ```toml
    [project]
    name = "swf-testbed"
    version = "0.1.0"
    description = "A meta-package to install and manage the ePIC Streaming Workflow Testbed."
    requires-python = ">=3.9"
    dependencies = [
        # List all components to be installed from the private package index
        "swf-common-lib",
        "swf-monitor",
        "swf-daqsim-agent",
        "swf-data-agent",
        "swf-processing-agent",
        "swf-fastmon-agent",
        "swf-mcp-agent",
        # CLI tool dependencies
        "typer[all]", # Using typer[all] installs optional deps like rich
        "supervisor"
    ]

    [project.scripts]
    # This creates the `swf-testbed` command in the user's PATH
    swf-testbed = "swf_testbed_cli.main:app"
    ```

2.  **Create the Management CLI:**
    A simple command-line tool (e.g., using `Typer`) will be created within
    this repository. It will provide commands for the end-user, such as:

    * `swf-testbed init`: Creates a local runtime environment, including a
      default `supervisord.conf` and a `logs` directory.
    * `swf-testbed start`: Starts the testbed services using `supervisord`.
    * `swf-testbed stop`: Stops the services.
    * `swf-testbed status`: Checks the status of the services.

## Phase 3: Private Package Distribution with GitHub Packages

To enable the simple `pip install swf-testbed` command for internal use, we will
use GitHub Packages as a private package index. This is the most seamless
approach for projects hosted on GitHub.

Below are the detailed, step-by-step instructions for both publishing packages
and consuming them.

### For Package Developers: How to Publish

These steps outline how to publish packages. The recommended approach for a team is to automate this process using GitHub Actions.

#### Recommended: Automated Publishing with GitHub Actions

For a robust and secure workflow, you should not publish packages from your local machine using a personal token. Instead, automate it with GitHub Actions.

1.  **Create a Workflow File:** In each component repository, create a file like `.github/workflows/publish-to-ghp.yml`.

2.  **Define the Workflow:** This workflow will trigger on a push to your main branch or when a new release is created. It will check out the code, build the package, and upload it to GitHub Packages.

    ```yaml
    # .github/workflows/publish-to-ghp.yml
    name: Publish Python Package to GHP

    on:
      push:
        branches:
          - main # Or your default branch

    jobs:
      publish:
        runs-on: ubuntu-latest
        permissions:
          contents: read
          packages: write # Required to publish packages
        steps:
          - uses: actions/checkout@v3
          - name: Set up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.9'
          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install build twine
          - name: Build package
            run: python -m build
          - name: Publish package
            run: twine upload --repository-url https://pypi.pkg.github.com/<OWNER> -u __token__ -p ${{ secrets.GITHUB_TOKEN }} dist/*
    ```

    *   Replace `<OWNER>` with your GitHub organization name (`bnlnpps`).
    *   The `GITHUB_TOKEN` is automatically created by Actions and has the necessary permissions. You do not need to create a PAT for this.

This ensures that your packages are published consistently and securely without relying on an individual's credentials.

#### Manual Publishing (for testing or one-offs)

If you need to publish a package manually, you can use a Personal Access Token (PAT).

##### Step 1: Create a Personal Access Token (PAT)

You need a PAT to authenticate with the GitHub Packages API.

1. Navigate to your GitHub **Settings**.
2. Go to **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
3. Click **Generate new token** (or **Generate new token (classic)**).
4. Give the token a descriptive name (e.g., `swf-package-publish`).
5. Set an expiration date for the token.
6. Select the **`write:packages`** scope. This scope is required to upload
   packages and automatically includes the `read:packages` permission.
7. Click **Generate token** and **copy the token immediately**. You will not be
   able to see it again. Store it securely.

##### Step 2: Link the Package to its Repository

To have your package's GitHub page show which repository it's connected to,
add the repository URL to your `pyproject.toml` file.

```toml
# In pyproject.toml
[project.urls]
"Repository" = "https://github.com/<OWNER>/<REPO_NAME>"
```

Replace `<OWNER>` and `<REPO_NAME>` with your GitHub organization/username and
repository name.

##### Step 3: Configure `twine` for Uploading

To simplify the upload process, create a `.pypirc` file in your home directory
(`~/.pypirc` on Linux/macOS). This file will store the configuration for `twine`.

```ini
[distutils]
index-servers =
    github

[github]
repository = https://pypi.pkg.github.com/<OWNER>
username = __token__
password = <YOUR_PAT>
```

* Replace `<OWNER>` with the name of the GitHub user or organization that owns
  the repository.
* Replace `<YOUR_PAT>` with the Personal Access Token you created in Step 1.
* The username must be `__token__`.

##### Step 4: Build and Upload the Package

Now you can build your package and upload it.

1. **Install build tools:**

   ```bash
   pip install build twine
   ```

2. **Build the distributions:** From the root of your package's repository, run:

   ```bash
   python -m build
   ```

   This will create a `dist/` directory containing the `.whl` (wheel) and
   `.tar.gz` (sdist) files.

3. **Upload to GitHub Packages:**

   ```bash
   twine upload --repository github dist/*
   ```

   `twine` will use the configuration from your `.pypirc` file to securely
   upload the package.

After a successful upload, you can view the package on your repository's main
page under the "Packages" section.

### For End-Users: How to Install

An end-user who wants to install `swf-testbed` needs to perform a simple,
one-time configuration.

#### Step 1: Create a Personal Access Token (PAT)

The user needs a PAT with permission to read packages.

1. Follow the same steps as above to create a PAT.
2. The only scope required is **`read:packages`**.
3. Copy the token and store it securely.

#### Step 2: Configure Pip

The user must configure `pip` to look for packages in the GitHub Packages index.
This is done by creating or editing the `pip.conf` file.

* **Location:**
  * macOS/Linux: `~/.pip/pip.conf`
  * Windows: `%APPDATA%\pip\pip.ini`

Add the following content to the file:

```ini
[global]
extra-index-url = https://<USER>:<TOKEN>@pypi.pkg.github.com/<OWNER>/
```

* Replace `<USER>` with the user's GitHub username.
* Replace `<TOKEN>` with the `read:packages` PAT they just created.
* Replace `<OWNER>` with the GitHub organization or user that owns the package
  repositories.

#### Step 3: Install the Package

After the one-time setup, installation is simple and clean:

```bash
pip install swf-testbed
```

`pip` will now be able to find and install `swf-testbed` and all its
dependencies from your private GitHub Packages index.

## The Final Workflow

With the packaging and distribution infrastructure in place, the end-user
workflow is exactly as intended:

1. **One-time `pip` configuration** (as described above).
2. **Installation:** `pip install swf-testbed`
3. **Initialization and Management:**

   ```bash
   mkdir my-testbed-runtime
   cd my-testbed-runtime
   swf-testbed init
   swf-testbed start
   ```

This provides a professional, secure, and maintainable installation path for the
entire testbed.

## Appendix: Alternative - Direct Git Installation

If setting up a private package index is not feasible, a fallback option is to
install packages directly from their Git repositories. This is less ideal as it
couples the installation process directly to the source code repository and can
be less secure if not managed carefully.

To install a package directly from a private GitHub repository:

```bash
pip install git+https://<TOKEN>@github.com/<OWNER>/<REPO_NAME>.git@<BRANCH_OR_TAG>
```

This would need to be done for every single component, making it far more
cumbersome for the end-user.

# Packaging and Distribution

## ⚠️ GitHub Packages Approach Deprecated

> **Note:** The previous approach using GitHub Packages as a private Python package registry is now **deprecated** for this project. Persistent 404 errors and authentication issues were encountered, and the process was unreliable. The recommended and working approach is to use [TestPyPI](https://test.pypi.org/) for internal testing and PyPI for production releases.

### Why Deprecated?
- GitHub Packages Python registry is less mature and has confusing authentication requirements.
- Error messages are often unhelpful (404/403) and difficult to debug.
- TestPyPI and PyPI are the standard, well-supported Python package registries.

### What to Use Instead
- Use [TestPyPI](https://test.pypi.org/) for testing your packaging and publishing workflow.
- Use [PyPI](https://pypi.org/) for production releases.
- See [`publishing_to_testpypi.md`](publishing_to_testpypi.md) for the recommended procedure.

---

## Old GitHub Packages Instructions (for reference only)

<details>
<summary>Show legacy instructions</summary>

- You must use a GitHub Personal Access Token (PAT) with `write:packages` and `repo` scopes.
- In your `.pypirc`, use `username = __token__` and `password = <your-github-pat>`.
- The package name in `pyproject.toml` must exactly match the repository name.
- See [GitHub Packages documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-python-registry) for more details.

</details>
