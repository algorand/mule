from termcolor import cprint
import os
import sys
import yaml

import mule.parser
import mule.validator as validator
import mule.util.yaml.env_var_loader as yaml_util
from mule.util import JobContext, file_util, prettify_json, update_dict
from mule.error import messages
from mule.task import Job

def main():
    args = mule.parser.parseArgs()
    try:
        mule_yamls = args.file
        if len(mule_yamls) == 0:
            mule_yamls.append('mule.yaml')
        mule_config = _read_mule_yamls(mule_yamls)
        agent_configs, jobs_config, task_configs = _get_configs(mule_config, raw=yaml_read_raw(args))

        if args.list_agents:
            _list_agents(agent_configs, args.verbose)
        elif args.list_jobs:
            _list_jobs(jobs_config, args.verbose)
        elif args.list_env:
            _list_env(agent_configs, jobs_config, task_configs, args.list_env, args.verbose)
        elif args.list_tasks:
            _list_tasks(task_configs, args.verbose)
        else:
            _execute_job(jobs_config, task_configs, agent_configs, args.JOB)
    except Exception as error:
        cprint(
            messages.MULE_DRIVER_EXCEPTION.format(args.JOB, args.file, error),
            'red',
            attrs=['bold'],
            file = sys.stderr
        )
        raise error

def _get_configs(mule_config, raw):
    parsed_mule_config = yaml_util.read_yaml(mule_config, raw)
    return validator.get_validated_mule_yaml(parsed_mule_config)

def _read_mule_yamls(mule_yamls):
    mule_config = {}
    for mule_yaml in mule_yamls:
        update_dict(
            mule_config,
            file_util.readYamlFile(mule_yaml),
            overwrite_lists=False
        )
    return mule_config

def _list_agents(agent_configs, verbose):
    for agent in agent_configs:
        if verbose:
            print(agent['name'], prettify_json(agent_configs))
        else:
            print(agent['name'])

def _list_env(agent_configs, jobs_config, task_configs, job_name, verbose):
    if not job_name in jobs_config:
        raise Exception(messages.JOB_NOT_FOUND.format(job_name))
    else:
        tasks = jobs_config[job_name]["tasks"]
        # Different tasks can have the same agent, so let's use a set.
        agents = set()

        for task in tasks:
            # Now that we have each task, loop over the yaml task configs (i.e., `tasks`)
            # to determine the agent defined for the specified tasks.
            for t_c in task_configs:
                # Recall that tasks may not have a "name" key.
                if (
                    # For example, "".join((t_c["task"], ".", t_c["name"])) matches `docker.Make.deb`.
                    "name" in t_c and "".join((t_c["task"], ".", t_c["name"])) == task or
                    t_c["task"] == task
                ):
                    agents.add(t_c["agent"])

        # If we're not concerned with knowing each agent config and whether or not
        # it has defined env vars (or anything else), we could improve this from
        # O(n^2) time to O(n) by simply checking if an agent_config["name"] is in
        # the set and then hoovering up the env vars (however, we wouldn't then know
        # anything about individual agents).
        #
        # However, it's useful to know the names of which agent configs DON'T
        # contain any env vars, for example, so then we can print that to STDOUT.
        items = {}
        for agent in agents:
            for a_c in agent_configs:
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
        return items

def _list_jobs(jobs_config, verbose):
    for job in jobs_config.keys():
        if verbose:
            print(job, prettify_json(jobs_config[job]))
        else:
            print(job)

def _list_tasks(task_configs, verbose):
    if verbose:
        print(prettify_json(task_configs))
    else:
        for task in task_configs:
            if 'name' in task.keys():
                print(f"{task['task']}.{task['name']}")
            else:
                print(task['task'])

def _execute_job(jobs_config, task_configs, agent_configs, job):
    if not job in jobs_config:
        raise Exception(messages.JOB_NOT_FOUND.format(job))
    job_config = jobs_config[job]
    job_config.update({
        'agent_configs': agent_configs,
        'task_configs': task_configs,
        'name': job
    })
    job = Job(job_config)
    job_context = JobContext(agent_configs)

    return job.execute(job_context)

def yaml_read_raw(args):
    return args.list_agents or args.list_env

