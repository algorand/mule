import yaml
import mule.parser
import mule.validator as validator
import mule.util.yaml.env_var_loader as yaml_util
from mule.util import JobContext
from mule.error import messages
from mule.task import Job
import os
from termcolor import cprint
import sys

def main():
    args = mule.parser.parseArgs()
    try:
        jobs_config, task_configs = validator.getValidatedMuleYaml(args.file)
        if not args.JOB in jobs_config:
            raise Exception(messages.JOB_NOT_FOUND.format(args.JOB))
        job_config = yaml_util.readYamlWithEnvVars(yaml.dump(jobs_config[args.JOB]))
        job_config.update({
            'task_configs': task_configs,
            'name': args.JOB
        })
        job = Job(job_config)
        job_context = JobContext()
        return job.execute(job_context)
    except Exception as error:
        cprint(
            messages.MULE_DRIVER_EXCEPTION.format(args.JOB, args.file, error),
            'red',
            attrs=['bold'],
            file = sys.stderr
        )
        raise error
