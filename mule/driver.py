from termcolor import cprint
import sys

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
        parsed_mule_config = yaml_util.read_yaml(mule_config, raw=yaml_read_raw(args))
        agent_configs, jobs_config, task_configs = validator.get_validated_mule_yaml(parsed_mule_config)
        if args.list_agents:
            _list_agents(agent_configs, args.verbose)
        elif args.list_jobs:
            _list_jobs(jobs_config, args.verbose)
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
    return args.list_agents

