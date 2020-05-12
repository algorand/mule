from mule.task import ITask
import mule.util.docker_util as docker
from mule.error import messages
from mule.util import update_dict
import re

class IDockerTask(ITask):

    required_typed_fields = [
        ('docker', dict),
        ('docker.image', str),
        ('docker.version', str),
    ]
    optional_typed_fields = [
        ('docker.workDir', str),
        ('docker.env', list),
        ('docker.shell', str),
    ]

    command = ''

    def __init__(self, args):
        super().__init__(args)
        self.docker = update_dict(
            {
                'workDir': '/project',
                'env': [],
                'volumes': [],
            },
            args['docker'],
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
        dockerEnvVarPattern = re.compile(r'.*=.+')
        self.docker['env'] = [envVar for envVar in self.docker['env'] if dockerEnvVarPattern.match(envVar)]

        for volume_index, volume in enumerate(self.docker['volumes']):
            if not type(volume) == str:
                raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                    self.getId(),
                    f"docker.env[{volume_index}]",
                    str,
                    type(volume)
                ))
        dockerVolumePattern = re.compile(r'.+:.+')
        self.docker['volumes'] = [volume for volume in self.docker['volumes'] if dockerVolumePattern.match(volume)]

        if not 'shell' in self.docker.keys():
            self.docker['shell'] = 'bash'

    def execute(self, job_context):
        super().execute(job_context)
        docker.run(
            f"{self.docker['image']}:{self.docker['version']}",
            [self.docker['shell'], '-c', self.command],
            self.docker['workDir'],
            self.docker['volumes'],
            self.docker['env'],
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
