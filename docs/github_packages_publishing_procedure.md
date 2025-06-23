# Procedure for Publishing to GitHub Packages

This document outlines the steps taken to attempt to publish Python packages (`swf-common-lib`, `swf-monitor`) to the `bnlnpps` organization's GitHub Packages registry. These steps resulted in a persistent `HTTP 404 Not Found` error.

## Method 1: Manual Upload with Twine

This method was attempted first to verify the basic authentication and upload process.

### 1. Package Building

The package was built from the root of the repository (`swf-common-lib`) using the standard Python build tool:

```bash
python -m build
```

This successfully created the `dist/` directory containing the source distribution (`.tar.gz`) and the built distribution (`.whl`).

### 2. Authentication Configuration (`~/.pypirc`)

A `~/.pypirc` file was configured to handle authentication with GitHub Packages. The Personal Access Token (PAT) was confirmed to have `write:packages` and `repo` scopes.

```ini
[distutils]
index-servers =
    github

[github]
repository = https://pypi.pkg.github.com/bnlnpps
username = __token__
password = <YOUR_PAT>
```

### 3. Upload Command

The `twine` tool was used to upload the built packages to the GitHub Packages registry associated with the `bnlnpps` organization.

```bash
twine upload --repository github dist/*
```

**Outcome:** This command consistently failed with an `HTTPError: 404 Not Found` error, indicating that the target repository could not be found or that write access was denied in a way that presented as a 404.

## Method 2: Automated Publishing with GitHub Actions

To eliminate local environment issues and use the recommended `GITHUB_TOKEN`, a GitHub Actions workflow was created.

### 1. Workflow File (`.github/workflows/publish-to-gpr.yml`)

A workflow was set up in the `swf-common-lib` repository to trigger on pushes to tags (e.g., `v0.0.8`).

The final version of the workflow file was:

```yaml
name: Publish Python Package to GPR

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

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

    - name: Publish package to GitHub Packages
      run: twine upload --repository-url https://pypi.pkg.github.com/bnlnpps dist/*
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Triggering the Workflow

The workflow was triggered by creating and pushing a new tag:

```bash
git tag v0.0.8
git push origin v0.0.8
```

**Outcome:** The workflow job also failed at the `twine upload` step with the same `HTTP 404 Not Found` error.

## Verification Steps Taken

The following items were verified and confirmed to be correct:

1.  **Organization Settings:** The `bnlnpps` organization successfully hosts packages from other repositories, confirming it is enabled for GitHub Packages.
2.  **Repository Name vs. Package Name:** The `name` in `pyproject.toml` (`swf-common-lib`) was confirmed to exactly match the GitHub repository name.
3.  **Authentication:** Read access was confirmed by successfully using `pip install` to download a package from the organization's registry using the same PAT.
4.  **Permissions:** The GitHub Actions workflow was explicitly granted `packages: write` permissions.

The persistent and unexplained 404 error suggests a repository-specific issue that is not visible through standard configuration settings.
