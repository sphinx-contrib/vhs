# Contributing to Sphinx VHS

## Set up your environment

We use [`uv`] and [`poe`] to run tasks, but it is possible to use pure pip as well.

[`uv`]: https://docs.astral.sh/uv/
[`poe`]: https://poethepoet.natn.io/index.html

### Using pip

1. Create a virtual environment with python `3.13` or newer
   (some of dev tools don't work with older pythons).

2. Make sure your pip is up to date:

   ```shell
   pip install -U pip
   ```

2. Install Sphinx VHS in development mode, and install dev dependencies:

   ```shell
   pip install -e . --group dev
   ```

3. Install pre-commit hooks:

   ```shell
   prek install
   ```

4. [Install `poe`], either globally or in virtual environment:

   ```shell
   pip install poethepoet
   ```

[Install `poe`]: https://poethepoet.natn.io/installation.html

### Using uv

1. Sync your virtual environment:

   ```shell
   uv sync
   ```

2. Install pre-commit hooks:

   ```shell
   uv run prek install
   ```

3. [Install `poe`] if you don't have it already:

   ```shell
   uv tool install poethepoet
   ```


## Run commands

We use `poe` for most of the tasks:

```shell
poe lint  # Lint and fix code style.
poe test  # Run tests.
poe test-all  # Run tests for all pythons.
```

You can see all commands in `poe`'s help:

```shell
poe --help
```


## Build docs

To build docs, you'll need to install a latest [`VHS`] release.
If you run linux, [`vhs`] (the python wrapper) will download the binaries for you,
otherwise you will have to install it yourself. Note that if you're running WSL
or other system that doesn't have a browser,
you might need to install additional packages:

```shell
sudo apt-get update
sudo apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxkbcommon0 libxdamage1 libgbm1 libpango1.0-0 libasound2
```

After that, use `poe` commands:

```shell
poe doc  # Build HTML.
poe doc-watch  # Run sphinx-autobuild.
```

The first build will take a couple of minutes to record terminal GIFs.

[`VHS`]: https://github.com/charmbracelet/vhs?tab=readme-ov-file#installation
[`vhs`]: https://github.com/taminomara/python-vhs


## Release

1. Update `CHANGELOG.md`.

   Changelog *must* have a section for the new release, otherwise the build
   will fail.

2. Push a git tag. You'll need a repository admin role to do so.

   All tags should start with prefix `v`, and follow semantic versioning guidelines.
   This, among other things, means that tags for beta-, post-, etc. releases
   should have form `v1.0.0-beta0` instead of Python's `v1.0.0b0`.

   You can use `poe release` to bump the version, create the release commit,
   and tag it in one step.

3. From here, release happens automatically. PyPi package will be uploaded from
   CI job, and documentation will be updated by Read the Docs build.
