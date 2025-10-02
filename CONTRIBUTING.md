# Contributing

## Set up your environment

1. Clone the repository.

2. Create a virtual environment with python `3.12` or newer.

3. Install Sphinx Vhs in development mode, and install dev dependencies:

   ```shell
   pip install -e . --group dev
   ```

4. Install pre-commit hooks:

   ```shell
   pre-commit install
   ```

## Run tests

To run tests, simply run `pytest` and `pyright`:

```shell
pytest  # Run unit tests.
pyright  # Run type check.
```

To fix code style, you can manually run pre-commit hooks:

```shell
pre-commit run -a  # Fix code style.
```

## Build docs

Just run `sphinx` as usual, nothing special is required:

```shell
cd docs/
make html
```

## Release

1. Update `changelog.md`. Make sure to update links at the end of the file.

   Changelog *must* have a section for the new release, otherwise the build
   will fail.

2. Push a git tag. You'll need a repository admin role to do so.

   All tags should start with prefix `v`, and follow semantic versioning guidelines.
   This, among other things, means that tags for beta-, post-, etc. releases
   should have form `v1.0.0-beta0` instead of Python's `v1.0.0b0`.

3. From here, release happens automatically. PyPi package will be uploaded from
   CI job, and documentation will be updated by Read the Docs build.
