import pytest

from mule.task import mule


@pytest.fixture(scope="module")
def mule_configs():
    return mule.get_configs("mule.yaml", raw=True)


@pytest.mark.parametrize("mule_yaml, raw", [
    ("mule.yaml", True),
    ("mule.yaml", False),
    (["mule.yaml"], True),
    (["mule.yaml"], False),
])
def test_get_configs(mule_yaml, raw):
    mule_configs = mule.get_configs(mule_yaml, raw)
    assert set(mule_configs.keys()) == set(["agents", "jobs", "tasks"])


def test_get_version():
    version = mule.get_version()
    # Assert that we're following semver.
    assert len(version.split(".")) == 3


def test_list_agents(mule_configs):
    agents = mule.list_agents(mule_configs.get("agents"))
    assert set(agents) == set(["deb", "rpm"])


# Applying `indirect` will reference the fixture.
# https://docs.pytest.org/en/latest/example/parametrize.html#apply-indirect-on-particular-arguments
@pytest.mark.parametrize("mule_configs, job, agent", [
    (mule_configs, "goodbye", ["deb"]),
    (mule_configs, "hello", ["deb"]),
    (mule_configs, "echo", []),
    (mule_configs, "double_dip", ["deb", "rpm"]),
], indirect=["mule_configs"])
def test_list_env(mule_configs, job, agent):
    env = mule.list_env(mule_configs, job)
    assert set(env.keys()) == set(agent)
    if len(agent):
        agent_keys = {key for ag in agent for key in env.get(ag).keys()}
        assert agent_keys == set(["NETWORK", "VERSION"])


def test_list_env_exception(mule_configs):
    job = "ddddderppppp"
    with pytest.raises(Exception) as exception_info:
        mule.list_env(mule_configs, job)
    assert exception_info.typename == "Exception"
    assert exception_info.match(f"Could not find job for name {job}")


def test_list_jobs(mule_configs):
    jobs = mule.list_jobs(mule_configs.get("jobs"))
    assert set(jobs) == set(["double_dip", "echo", "echoes", "goodbye", "hello"])


def test_list_tasks(mule_configs):
    tasks = mule.list_tasks(mule_configs.get("tasks"))
    assert set(tasks) == set(["docker.Make.hello", "docker.Make.goodbye", "docker.Make.play", "Echo.A", "Echo.B", "Echo.C"])
