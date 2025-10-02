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
