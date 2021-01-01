from termcolor import cprint
import os
import sys
import yaml

from mule.error import messages
from mule.logger import logger
from mule.task import Job
from mule.util import JobContext, file_util, prettify_json, update_dict
import mule.parser
import mule.util.yaml.env_var_loader as yaml_util
import mule.validator as validator


def main():
    args = mule.parser.parseArgs()
    try:
        mule_yamls = args.file
        if not len(mule_yamls):
            mule_yamls.append('mule.yaml')

        if args.recipe:
            plugins = mule.validator.get_plugin("saddle")
            if not len(plugins):
                raise Exception(messages.PLUGIN_NOT_FOUND.format("saddle"))
            else:
                saddle = plugins[0]
                out = saddle.compile(args.recipe)
                job_yaml = yaml.safe_load(out)
                job_configs = yaml_util.read_yaml(job_yaml.get("items"), raw=False)
                for j_c in job_configs:
                    _execute_job(j_c)
                return

        if args.verbose:
            logger.setLevel(10)

        mule_config = _get_configs(
                _read_mule_yamls(mule_yamls),
                raw=yaml_read_raw(args))

        if args.list_agents:
            _list_agents(mule_config['agents'])
        elif args.list_jobs:
            _list_jobs(mule_config['jobs'])
        elif args.list_env:
            _list_env(mule_config, args.list_env, args.verbose)
        elif args.list_tasks:
            _list_tasks(mule_config['tasks'])
        else:
            if args.job not in mule_config['jobs']:
                raise Exception(messages.JOB_NOT_FOUND.format(args.job))
            job_config =_get_job_config(mule_config, args.job)
            _execute_job(job_config)
    except Exception as error:
        cprint(
            messages.MULE_DRIVER_EXCEPTION.format(args.job, args.file, error),
            'red',
            attrs=['bold'],
            file=sys.stderr
        )
        raise error


def _execute_job(job_config):
    job = Job(job_config)
    job_context = JobContext(job_config)
    return job.execute(job_context)


def _get_configs(mule_config, raw):
    parsed_mule_config = yaml_util.read_yaml(mule_config, raw)
    return validator.get_validated_mule_yaml(parsed_mule_config)


def _get_job_config(mule_config, job):
    job_def = mule_config["jobs"].get(job)
    job_configs = job_def.get("configs", {})
    tasks = job_def.get("tasks", [])
    task_configs = []
    agents = []
    for job_task in tasks:
        name, task = _get_task(mule_config, job_task)
        task_configs.append(task)
        if "dependencies" in task:
            for dependency in task["dependencies"]:
                _, task = _get_task(mule_config, dependency)
                task_configs.append(task)
        # Recall not all tasks have an agent!
        if "agent" in task and job_task == name:
            agent = task["agent"]
            agents = [item for item in mule_config["agents"] if task["agent"] == item["name"]]
    return {
        "name": job,
        "configs": job_configs,
        "agents": agents,
        "tasks": tasks,
        "task_configs": task_configs,
    }


def _get_task(mule_config, job_task):
    for task in mule_config["tasks"]:
        if "name" in task:
            name = ".".join((task["task"], task["name"]))
        else:
            name = task["task"]
        if name == job_task:
            return name, task


def _list_agents(agent_configs):
    for agent in agent_configs:
        #        logger.debug(agent['name'], prettify_json(agent))
        logger.debug(prettify_json(agent))
        print(agent['name'])


def _list_env(mule_config, job_name, verbose):
    if job_name not in mule_config["jobs"]:
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

            print(yaml.dump(items))
        else:
            print(f"The job `{job_name}` has no agents and no environment.")
        return items


def _list_jobs(jobs_config):
    for job in jobs_config.keys():
        logger.debug(job, prettify_json(jobs_config[job]))
        print(job)


def _list_tasks(task_configs):
    logger.debug(prettify_json(task_configs))
    for task in task_configs:
        if 'name' in task.keys():
            print(f"{task['task']}.{task['name']}")
        else:
            print(task['task'])


def _read_mule_yamls(mule_yamls):
    mule_config = {}
    for mule_yaml in mule_yamls:
        update_dict(
            mule_config,
            file_util.read_yaml_file(mule_yaml),
            overwrite_lists=False
        )
    return mule_config


def yaml_read_raw(args):
    return args.list_agents or args.list_env
