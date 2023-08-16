import pytest
from mochicards.client import MochiClient


@pytest.fixture
def mochi_client():
    return MochiClient()
