import os
import time
from pydoc import locate

from mule.error import messages
from mule.util import file_util
from mule.util import get_dict_value

DEFAULT_MULE_CONFIGS = {
    'packages': [
        'mule.task'
    ]
}

DEFAULT_MULE_CONFIG_PATH = "~/.mule/config.yaml"

def getValidatedMuleConfigFile():
    config_file_path = os.path.abspath(os.path.expanduser(DEFAULT_MULE_CONFIG_PATH))
    mule_configs = DEFAULT_MULE_CONFIGS
    if os.path.isfile(config_file_path):
        mule_configs_from_file = file_util.readYamlFile(config_file_path)
        mule_configs.update(mule_configs_from_file)
    return mule_configs

def getValidatedMuleYaml(mule_config):
    mule_config_keys = mule_config.keys()

    if not 'jobs' in mule_config_keys:
        raise Exception(messages.FIELD_NOT_FOUND.format('jobs'))
    if not 'tasks' in mule_config_keys:
        raise Exception(messages.FIELD_NOT_FOUND.format('tasks'))

    task_configs = mule_config['tasks']
    jobs_configs = mule_config['jobs']
    agent_configs = mule_config['agents'] if 'agents' in mule_config else []

    try:
        validateJobConfigs(jobs_configs)
    except Exception as error:
        raise Exception(messages.FIELD_VALUE_COULD_NOT_BE_VALIDATED.format(
            'jobs',
            str(error)
        ))

    try:
        validateTaskConfigs(task_configs)
    except Exception as error:
        raise Exception(messages.FIELD_VALUE_COULD_NOT_BE_VALIDATED.format(
            'tasks',
            str(error)
        ))

    return jobs_configs, task_configs, agent_configs

def validateJobConfigs(job_configs):
    if not type(job_configs) == dict:
        raise Exception(messages.FIELD_VALUE_WRONG_TYPE.format('jobs', dict, type(job_configs)))

def validateTaskConfigs(task_configs):
    if not type(task_configs) == list:
        raise Exception(messages.FIELD_VALUE_WRONG_TYPE.format('tasks', list, type(task_configs)))
    for task_config_index, task_config in enumerate(task_configs):
        if not type(task_config) == dict:
            raise Exception(messages.FIELD_VALUE_WRONG_TYPE.format(f"tasks[{task_config_index}]", dict, type(task_configs)))

def validateTypedFields(task_id, task_fields, task_required_typed_fields, task_optional_typed_fields):
    for required_field, required_field_type in task_required_typed_fields:
        required_field_index = required_field.split('.')
        required_field_value = get_dict_value(task_fields, required_field_index)
        if required_field_value is None:
            raise Exception(messages.TASK_MISSING_REQUIRED_FIELDS.format(
                task_id,
                required_field,
                task_required_typed_fields,
            ))
        if not type(required_field_value) == required_field_type:
            raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                task_id,
                required_field,
                required_field_type,
                type(required_field_value)
            ))
    for optional_field, optional_field_type in task_optional_typed_fields:
        optional_field_index = optional_field.split('.')
        optional_field_value = get_dict_value(task_fields, optional_field_index)
        if not optional_field_value is None:
            if not type(optional_field_value) == optional_field_type:
                raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                    task_id,
                    optional_field,
                    optional_field_type,
                    type(optional_field_value)
                ))

def validateTaskConfig(task_config):
    if not 'task' in task_config:
        raise Exception(messages.TASK_FIELD_MISSING)

def getValidatedTask(task_config):
    mule_config = getValidatedMuleConfigFile()
    task_name = task_config['task']
    for package in mule_config['packages']:
        task_obj = locate(f"{package}.{task_name}")
        if not task_obj is None:
            return task_obj(task_config)
    raise Exception(messages.CANNOT_LOCATE_TASK.format(task_name))

def getValidatedTaskDependencyChain(job_context, dependency_edges):
    # This is basically dfs, so these tuples represent edges
    # Index 0 is the requested task and index 1 is the
    # requesting task. Organizing the problem this way helps
    # with cycle detection. I'm reversing this list so
    # it starts out as stack
    dependency_edges.reverse()
    tasks_tbd = []
    seen_dependency_edges = []
    # Give mule 10 seconds to decipher dependency tree
    # if it takes longer than this, mule is probably in
    # an infinite loop
    timeout = time.time() + 10
    while len(dependency_edges) > 0:
        if time.time() > timeout:
            raise Exception(messages.TASK_DEPENDENCY_CHAIN_TIMEOUT)
        dependency_edge = dependency_edges.pop(0)
        if dependency_edge in seen_dependency_edges:
            raise Exception(messages.TASK_DEPENDENCY_CYCLIC_DEPENDENCY.format(dependency_edge[1], dependency_edge[0]))
        seen_dependency_edges.append(dependency_edge)
        task_context = job_context.get_field(f"{dependency_edge[0]}")
        if task_context is None:
            raise Exception(messages.CANNOT_LOCATE_TASK_CONFIGS.format(dependency_edge[1], dependency_edge[0]))
        if not 'completed' in task_context:
            if not 'task' in task_context:
                task_context['task'] = getValidatedTask(task_context['inputs'])
            if task_context['task'] in tasks_tbd:
                # Our graph has different nodes with the same name.
                # These nodes are the same as far as we're concerned
                # so when we see repeats, we'll delete the earlier
                # nodes. The ones that show up later get executed
                # first, and we only want these to be executed once.
                tasks_tbd.remove(task_context['task'])
            tasks_tbd.append(task_context['task'])
            for dependency_edge in task_context['task'].getDependencyEdges():
                dependency_edges.insert(0, dependency_edge)
    # Reversing the list because we started with
    # the targeted task and ended with the earliest
    # dependency in the chain. Since these are
    # dependencies we're working with, we want
    # those executed first.
    tasks_tbd.reverse()
    return tasks_tbd

def validateRequiredTaskFieldsPresent(task_id, fields, required_fields):
    for field in required_fields:
        if not field in fields.keys():
            raise Exception(messages.TASK_MISSING_REQUIRED_FIELDS.format(
                task_id,
                field,
                str(required_fields)
            ))

