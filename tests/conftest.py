import pytest

from mule import mule


@pytest.fixture(scope="module")
def mule_configs():
    return mule.get_configs("mule.yaml", raw=True)
