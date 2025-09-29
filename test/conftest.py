import pytest
import pathlib

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture(scope="session")
def rootdir():
    return pathlib.Path(__file__).parent / "roots"
