import yaml
from mule.task.mule import get_configs, list_agents, list_env, list_jobs, list_tasks
from mule.task.error import messages
from mule.logger import logger, start_debug
import mule.task.parser
from mule.task import Job
from mule.util import JobContext, prettify_json
import mule.util.yaml.env_var_loader as yaml_util
import mule.task.validator


def _execute_job(job_config):
    job = Job(job_config)
    job_context = JobContext(job_config)
    return job.execute(job_context)


def _get_job_config(mule_config, job):
    job_def = mule_config["jobs"].get(job)
    job_configs = job_def.get("configs", {})
    tasks = job_def.get("tasks", [])
    mule_agents = mule_config.get("agents", [])
    task_configs = []
    agents = []
    for job_task in tasks:
        task = _get_task(mule_config, job_task)
        task_configs.append(task)
        if "dependencies" in task:
            for dependency in task["dependencies"]:
                task = _get_task(mule_config, dependency)
                task_configs.append(task)
    if len(mule_agents):
        all_agents = {}
        for agent in mule_agents:
            all_agents[agent.get("name")] = agent
        agents_names = list({task.get("agent") for task in task_configs if task.get("agent")})
        agents = [all_agents[name] for name in agents_names]
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
            return task


def _yaml_read_raw(args):
    return args.list_agents or args.list_env


def main():
    args = mule.task.parser.parseArgs()
    try:
        mule_yamls = args.file
        if not len(mule_yamls):
            mule_yamls.append("mule.yaml")

        if args.recipe:
            plugins = mule.validator.get_plugin("saddle")
            if not len(plugins):
                raise Exception(messages.PLUGIN_NOT_FOUND.format("saddle"))
            else:
                saddle = plugins[0]
                out = saddle.compiler.compile(args.recipe)
                job_yaml = yaml.safe_load(out)
                job_configs = yaml_util.read_yaml(job_yaml.get("items"), raw=False)
                for j_c in job_configs:
                    _execute_job(j_c)
                return

        if args.debug:
            start_debug(args)

        mule_config = get_configs(mule_yamls, raw=_yaml_read_raw(args))

        if args.list_agents:
            if args.verbose:
                print(prettify_json({agent.get("name"): agent for agent in mule_config.get("agents")}))
            else:
                print("\n".join(list_agents(mule_config.get("agents"))))
        elif args.list_jobs:
            if args.verbose:
                jobs_config = mule_config.get("jobs")
                print(prettify_json({job: jobs_config.get(job) for job in jobs_config}))
            else:
                print("\n".join(list_jobs(mule_config.get("jobs"))))
        elif args.list_env:
            print(prettify_json(list_env(mule_config, args.list_env, args.verbose)))
        elif args.list_tasks:
            if args.verbose:
                print(prettify_json({task.get("name"): task for task in mule_config.get("tasks")}))
            else:
                print("\n".join(list_tasks(mule_config.get("tasks"))))
        else:
            if args.job not in mule_config.get("jobs"):
                raise Exception(messages.JOB_NOT_FOUND.format(args.job))
            job_config =_get_job_config(mule_config, args.job)
            _execute_job(job_config)
    except Exception as error:
        logger.error(messages.MULE_DRIVER_EXCEPTION.format(args.job, args.file, error))
        raise error
