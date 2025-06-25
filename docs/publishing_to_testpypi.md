# Publishing to TestPyPI

This document describes the **recommended and working procedure** for publishing your Python package to [TestPyPI](https://test.pypi.org/), a separate instance of the Python Package Index for testing purposes.

## 1. Create a TestPyPI Account
- Go to [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/) and create an account.
- Verify your email address.

## 2. Configure `~/.pypirc` for API Token
Add the following to your `~/.pypirc` file (create it if it doesn't exist):

```ini
[distutils]
index-servers =
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-api-token>
```
- **username must be `__token__`** (literally, two underscores on each side of `token`).
- **password must be your TestPyPI API token** (not your password).
- You can generate a token at [TestPyPI API tokens](https://test.pypi.org/manage/account/token/).

## 3. Bump the Version
- Each upload to TestPyPI must use a unique version number in your `pyproject.toml`:
  ```toml
  version = "<new-version>"
  ```

## 4. Build the Package
From the root of your package directory:

```bash
pip install --upgrade build
python -m build
```

## 5. Upload to TestPyPI

```bash
pip install --upgrade twine
twine upload --repository testpypi dist/*
```

## 6. Install from TestPyPI
To test installation from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ <your-package-name>
```

## Notes
- TestPyPI is for testing only. Packages may be deleted at any time.
- Use a unique version number for each upload.
- If you want to automate this with GitHub Actions, update your workflow to use the TestPyPI repository URL and credentials.
