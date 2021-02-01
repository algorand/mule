import os

import mule
from mule.task.error import messages
from mule.util import file_util, update_mule_file
import mule.util.yaml.env_var_loader as yaml_util
import mule.task.validator


def _read_mule_yamls(mule_yamls):
    if type(mule_yamls) is not list:
        mule_yamls = [mule_yamls]
    mule_config = {}
    for mule_yaml in mule_yamls:
        update_mule_file(
            mule_config,
            file_util.read_yaml_file(mule_yaml),
            overwrite_lists=False
        )
    return mule_config


def get_configs(mule_yamls, raw):
    mule_config = _read_mule_yamls(mule_yamls)
    parsed_mule_config = yaml_util.read_yaml(mule_config, raw)
    return mule.validator.get_validated_mule_yaml(parsed_mule_config)


def get_version():
    return mule.__version__


def list_agents(agent_configs):
    return [agent.get("name") for agent in agent_configs]


def list_env(mule_config, job_name, verbose=False):
    if job_name not in mule_config.get("jobs"):
        raise Exception(messages.JOB_NOT_FOUND.format(job_name))
    else:
        tasks = mule_config["jobs"][job_name]["tasks"]
        # Different tasks can have the same agent, so let's use a set.
        agents = set()

        for task in tasks:
            # Now that we have each task, loop over the yaml task configs (i.e., `tasks`)
            # to determine the agent defined for the specified tasks.
            for task_config in mule_config["tasks"]:
                # Recall that tasks may not have a "name" key.
                if (
                    # For example, "".join((task_config["task"], ".", task_config["name"])) matches `docker.Make.deb`.
                    "name" in task_config and "".join((task_config["task"], ".", task_config["name"])) == task or
                    task_config["task"] == task
                ):
                    if "agent" in task_config:
                        agents.add(task_config["agent"])

        items = {}
        if len(agents):
            # If we're not concerned with knowing each agent config and whether or not
            # it has defined env vars (or anything else), we could improve this from
            # O(n^2) time to O(n) by simply checking if an agent_config["name"] is in
            # the set and then hoovering up the env vars (however, we wouldn't then know
            # anything about individual agents).
            #
            # However, it's useful to know the names of which agent configs DON'T
            # contain any env vars, for example, so then we can print that to STDOUT.
            for agent in agents:
                for a_c in mule_config["agents"]:
                    if agent == a_c["name"]:
                        if "env" in a_c and a_c["name"] in agents:
                            envs = a_c['env']
                            # Only evaluate the env vars if `verbose` flag is set.
                            if verbose:
                                envs = []
                                for env in a_c["env"]:
                                    [name, value] = env.split("=")
                                    envs.append("=".join((name, os.path.expandvars(value))))
                            items[agent] = envs
                        else:
                            items[agent] = None
        return items


def list_jobs(jobs_config):
    return [job for job in jobs_config.keys()]


def list_tasks(task_configs):
    return [f"{task.get('task')}.{task.get('name')}" if "name" in task.keys() else task.get("task") for task in task_configs]
