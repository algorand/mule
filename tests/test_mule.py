from mule import mule


def test_get_configs(mule_configs):
    assert list(mule_configs.keys()) == ["agents", "jobs", "tasks"]


def test_get_version():
    version = mule.get_version()
    # Assert that we're following semver.
    assert len(version.split(".")) == 3


def test_list_agents(mule_configs):
    agents = mule.list_agents(mule_configs.get("agents"))
    assert agents == ["deb", "rpm"]


def test_list_env(mule_configs):
    env = mule.list_env(mule_configs, "goodbye")
    agents = env.keys()
    assert len(agents) == 1
    assert list(agents) == ["deb"]
    agent_keys = env.get("deb").keys()
    assert len(agent_keys) == 2
    assert list(agent_keys) == ["NETWORK", "VERSION"]


def test_list_jobs(mule_configs):
    jobs = mule.list_jobs(mule_configs.get("jobs"))
    assert jobs == ["echo", "echoes", "goodbye", "hello"]


def test_list_tasks(mule_configs):
    tasks = mule.list_tasks(mule_configs.get("tasks"))
    assert tasks == ["docker.Make.hello", "docker.Make.goodbye", "Echo.A", "Echo.B", "Echo.C"]
