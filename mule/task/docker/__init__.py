from mule.task import ITask
import mule.util.docker_util as docker
from mule.error import messages
from mule.util import update_dict

class IDockerTask(ITask):

    required_typed_fields = [
        ('docker', dict),
        ('docker.image', str),
        ('docker.version', str),
    ]
    optional_typed_fields = [
        ('docker.workDir', str),
        ('docker.env', list),
    ]

    command = ''

    def __init__(self, args):
        super().__init__(args)
        self.docker = update_dict(
            {
                'workDir': '/project',
                'env': [],
            },
            args['docker']
        )
        self.validateDockerConfigs()

    def validateDockerConfigs(self):
        # Validate docker env var onfigs are all strings
        for env_var_index, env_var in enumerate(self.docker['env']):
            if not type(env_var) == str:
                raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                    self.getId(),
                    f"docker.env[{env_var_index}]",
                    str,
                    type(env_var)
                ))

    def execute(self, job_context):
        super().execute(job_context)
        docker.run(
            f"{self.docker['image']}:{self.docker['version']}",
            ["bash", "-c", self.command],
            self.docker['workDir'],
            self.docker['env']
        )

class Make(IDockerTask):

    required_fields = [
        'target',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.target = args['target']
        self.command = f"make {self.target}"

    def execute(self, job_context):
        super().execute(job_context)

class Shell(IDockerTask):

    required_fields = [
        'command',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.command = args['command']

    def execute(self, job_context):
        super().execute(job_context)

class Version(ITask):

    required_fields = [
        'arch',
        'configFilePath',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.arch = args['arch']
        self.configFilePath = args['configFilePath']
    
    def execute(self, job_context):
        super().execute(job_context)
        version = docker.getVersion(self.arch, self.configFilePath)
        return {
            'version': version
        }
