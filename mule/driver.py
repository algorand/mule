import yaml
import mule.parser
import mule.validator as validator
import mule.util.yaml.mule_loader as yaml_util
from mule.util import JobContext, file_util
from mule.error import messages
from mule.task import Job
from termcolor import cprint
import sys

def main():
    args = mule.parser.parseArgs()
    try:
        parsed_mule_config = yaml_util.readYamlWithEnvVars(args.file)
        jobs_config, task_configs = validator.getValidatedMuleYaml(parsed_mule_config)
        if args.list_jobs:
            _list_jobs(jobs_config)
        elif args.list_tasks:
            _list_tasks(task_configs)
        else:
            _execute_job(jobs_config, task_configs, args.JOB)
    except Exception as error:
        cprint(
            messages.MULE_DRIVER_EXCEPTION.format(args.JOB, args.file, error),
            'red',
            attrs=['bold'],
            file = sys.stderr
        )
        raise error

def _list_jobs(jobs_config):
    for job in jobs_config.keys():
        print(job)

def _list_tasks(task_configs):
    for task in task_configs:
        if 'name' in task.keys():
            print(f"{task['task']}.{task['name']}")
        else:
            print(task['task'])

def _execute_job(jobs_config, task_configs, job):
    if not job in jobs_config:
        raise Exception(messages.JOB_NOT_FOUND.format(job))
    job_config = jobs_config[job]
    job_config.update({
        'task_configs': task_configs,
        'name': job
    })
    job = Job(job_config)
    job_context = JobContext()
    return job.execute(job_context)

