import os

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def test_env():
    os.environ = {"SENTRY_DSN": None, "WORKSPACE": "test"}
    yield


@pytest.fixture()
def runner():
    return CliRunner()
