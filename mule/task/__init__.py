import time

import pystache

import mule.validator as validator
from mule.error import messages

import ipdb

class ITask:
    required_fields = []
    required_typed_fields = []
    optional_typed_fields = []
    dependencies = []

    def __init__(self, job_config):
        package_ref = self.__class__.__module__.replace('mule.task', '')
        self.task_id = f"{package_ref}.{self.__class__.__name__}".lstrip('.')
        # Include name in task id if one is provided
        if 'name' in job_config:
            self.task_id = f"{self.task_id}.{job_config['name']}"
        if 'dependencies' in job_config:
            self.dependencies = job_config['dependencies']
        validator.validate_required_tasks_fields_present(
            self.task_id,
            job_config,
            self.required_fields
        )
        validator.validate_typed_fields(
            self.task_id,
            job_config,
            self.required_typed_fields,
            self.optional_typed_fields
        )

    def get_id(self):
        return self.task_id

    def evaluate_output_fields(self, job_fields):
        ignoredFields = ['dependencies', 'required_fields', 'task_id', 'task_configs']
        fieldDicts = [self.__dict__]
        timeout = time.time() + 10
        while len(fieldDicts) > 0:
            if time.time() > timeout:
                raise Exception(messages.TASK_FIELD_EVALUATION_TIMEOUT.format(self.get_id()))
            fieldDict = fieldDicts.pop(0)
            for field in fieldDict.keys():
                if field not in ignoredFields:
                    field_value = fieldDict[field]
                    if type(field_value) is str:
                        fieldDict[field] = pystache.render(field_value, job_fields)
                    if type(field_value) is list:
                        for element_index, element in enumerate(field_value):
                            if type(element) is str:
                                fieldDict[field][element_index] = pystache.render(element, job_fields)
                            elif type(element) is dict:
                                fieldDicts.append(element)
                    elif type(field_value) is dict:
                        fieldDicts.append(fieldDict[field])

    def get_dependencies(self):
        if type(self.dependencies) is str:
            return self.dependencies.split(' ')
        elif type(self.dependencies) is list:
            return self.dependencies
        return []

    def get_dependency_edges(self):
        dependency_edges = []
        for dependency in self.get_dependencies():
            dependency_edges.append((dependency, self.get_id()))
        return dependency_edges

    def execute(self, job_context):
        self.evaluate_output_fields(job_context.get_fields())


class Job(ITask):
    required_fields = [
        'tasks',
        'task_configs'
    ]

    required_typed_fields = [('tasks', list)]
    optional_typed_fields = [
        ('agent_configs', list),
        ('configs', dict)
    ]

    def __init__(self, job_config):
        super().__init__(job_config)
        self.dependencies = job_config['tasks']

    def execute(self, job_context):
        super().execute(job_context)
        self.build_job_context(job_context)
        tasks_tbd = validator.get_validated_task_dependency_chain(job_context, self.get_dependency_edges())
        for task in tasks_tbd:
            task_outputs = task.execute(job_context)
            task_id = task.get_id()
            job_context.add_field(f"{task_id}.outputs", task_outputs)
            job_context.add_field(f"{task_id}.completed", True)

    def build_job_context(self, job_context):
        for task_config in job_context.get_field('task_configs'):
            task_config.update(job_context.get_field('configs'))
            validator.validateTaskConfig(task_config)
            if 'name' in task_config:
                job_context.add_field(f"{task_config['task']}.{task_config['name']}.inputs", task_config)
            else:
                job_context.add_field(f"{task_config['task']}.inputs", task_config)


class HelloWorld(ITask):
    def execute(self, job_context):
        super().execute(job_context)
        print('Hello World!')


class Echo(ITask):
    required_fields = [
        'message'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.message = args['message']

    def execute(self, job_context):
        super().execute(job_context)
        print(self.message)
        return {
            'message': self.message
        }
