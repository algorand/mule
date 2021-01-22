import pytest

from mule import mule
from mule.task.docker import Make


@pytest.fixture(scope="module")
def mule_make_instance():
    mule_configs = mule.get_configs("docker.yaml", raw=True)
    deb = mule_configs.get("tasks")[0]
    return Make(deb)


# This tests both lists and dicts.
@pytest.mark.parametrize("mule_make_instance, block, delimiter", [
    (mule_make_instance, ["FOO=foo", "BAR=bar"], "="),
    (mule_make_instance, ["FOO=foo", "", "BAR=bar"], "="),
    (mule_make_instance, ["", "FOO=foo", "", "BAR=bar", ""], "="),
    (mule_make_instance, ["", "", "FOO=foo", "", "BAR=bar", ""], "="),
    (mule_make_instance, ["", "", "", "", "", "FOO=foo", "BAR=bar"], "="),
    (mule_make_instance, {"FOO": "foo", "BAR": "bar"}, ":"),
    (mule_make_instance, {"FOO": "foo", "QUUX": "", "BAR": "bar"}, ":"),
    (mule_make_instance, {"QUUX": "", "FOO": "foo", "ZIP": "", "BAR": "bar", "DERP": ""}, ":"),
    (mule_make_instance, {"KILGORE": "", "TROUT": "", "FOO": "foo", "ZIP": "", "BAR": "bar", "": ""}, ":"),
], indirect=["mule_make_instance"])
def test_format_block_list(mule_make_instance, block, delimiter):
    formatted_list = mule_make_instance.format_block(block, delimiter)
    assert formatted_list == [f"FOO{delimiter}foo", f"BAR{delimiter}bar"]
