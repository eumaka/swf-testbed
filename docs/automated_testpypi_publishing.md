# Automated Publishing to TestPyPI with GitHub Actions

This document details the procedure for automatically publishing Python packages to TestPyPI using a GitHub Actions workflow. This is the recommended method for releasing new versions of components like `swf-common-lib`.

The process relies on a workflow that triggers when a new version tag (e.g., `v0.0.10`) is pushed to the repository.

## 1. GitHub Actions Workflow

The core of the automation is the `.github/workflows/publish-to-testpypi.yml` file.

```yaml
name: Publish Python Package to TestPyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read

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

    - name: Publish package to TestPyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.TESTPYPI_API_TOKEN }}
      run: twine upload --repository testpypi dist/*
```

### Key Components:

- **`on: push: tags: - 'v*'`**: This trigger ensures the workflow only runs when a tag starting with `v` is pushed.
- **`TWINE_USERNAME: __token__`**: This is the critical setting for authenticating with TestPyPI's API. The username must be the literal string `__token__`.
- **`TWINE_PASSWORD: ${{ secrets.TESTPYPI_API_TOKEN }}`**: The password must be a TestPyPI API token, stored as an encrypted secret in the GitHub repository's settings.

## 2. Repository Secret Configuration

For the workflow to authenticate, you must create a repository secret named `TESTPYPI_API_TOKEN`.

1.  **Generate a Token**: Go to your TestPyPI account settings and generate a new API token: [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/).
2.  **Add to GitHub**: In your GitHub repository, go to `Settings` > `Secrets and variables` > `Actions`. Click `New repository secret` and add the token with the name `TESTPYPI_API_TOKEN`.

## 3. Publishing Workflow

Once the workflow and secret are in place, publishing a new version is simple:

1.  **Increment Version**: Update the `version` in your `pyproject.toml` file.
    ```toml
    # pyproject.toml
    version = "0.0.11"
    ```
2.  **Commit the Change**:
    ```bash
    git commit -am "Increment version to 0.0.11"
    ```
3.  **Tag the Commit**: Create a new git tag that matches the version number.
    ```bash
    git tag v0.0.11
    ```
4.  **Push to GitHub**: Push the commit and the new tag.
    ```bash
    git push && git push --tags
    ```

Pushing the tag will automatically trigger the GitHub Action, which builds the package and publishes it to TestPyPI. You can monitor its progress in the "Actions" tab of your repository.
