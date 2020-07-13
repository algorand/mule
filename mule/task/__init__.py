import time

import pystache

import mule.validator as validator
from mule.error import messages
from mule.util import update_dict

class ITask:

    required_fields = []
    required_typed_fields = []
    optional_typed_fields = []
    dependencies = []

    def __init__(self, args):
        package_ref = self.__class__.__module__.replace('mule.task', '')
        self.task_id = f"{package_ref}.{self.__class__.__name__}".lstrip('.')
        # Include name in task id if one is provided
        if 'name' in args:
            self.task_id =  f"{self.task_id}.{args['name']}"
        if 'dependencies' in args:
            self.dependencies = args['dependencies']
        validator.validateRequiredTaskFieldsPresent(
            self.task_id,
            args,
            self.required_fields
        )
        validator.validateTypedFields(
            self.task_id,
            args,
            self.required_typed_fields,
            self.optional_typed_fields
        )

    def getId(self):
        return self.task_id

    def evaluateOutputFields(self, job_context):
        ignoredFields = ['dependencies', 'required_fields', 'task_id', 'task_configs']
        fieldDicts = [self.__dict__]
        timeout = time.time() + 10
        job_fields = job_context.get_fields()
        while len(fieldDicts) > 0:
            if time.time() > timeout:
                raise Exception(messages.TASK_FIELD_EVALUATION_TIMEOUT.format(self.getId()))
            fieldDict = fieldDicts.pop(0)
            for field in fieldDict.keys():
                if not field in ignoredFields:
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

    def getDependencies(self):
        if type(self.dependencies) is str:
            return self.dependencies.split(' ')
        elif type(self.dependencies) is list:
            return self.dependencies
        return []

    def getDependencyEdges(self):
        dependency_edges = []
        for dependency in self.getDependencies():
            dependency_edges.append((dependency, self.getId()))
        return dependency_edges

    def execute(self, job_context):
        self.evaluateOutputFields(job_context)


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

    def __init__(self, args):
        super().__init__(args)
        self.dependencies = args['tasks']
        self.task_configs = args['task_configs']
        self.job_configs = args['configs'] if 'configs' in args else {}
        if 'agent_configs' in args:
            self.agent_configs = args['agent_configs']

    def execute(self, job_context):
        super().execute(job_context)
        self.buildJobContext(job_context)
        tasks_tbd = validator.getValidatedTaskDependencyChain(job_context, self.getDependencyEdges())
        for task in tasks_tbd:
            task_outputs = task.execute(job_context)
            task_id = task.getId()
            job_context.add_field(f"{task_id}.outputs", task_outputs)
            job_context.add_field(f"{task_id}.completed", True)

    def buildJobContext(self, job_context):
        for task_config in self.task_configs:
            update_dict(task_config, self.job_configs)
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
