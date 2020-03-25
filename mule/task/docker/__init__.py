from mule.task import ITask
import mule.util.docker_util as docker
from mule.error import messages

class DockerTask(ITask):

    required_typed_fields = [
        ('docker', dict),
        ('docker.image', str),
        ('docker.version', str),
    ]
    optional_typed_fields = [
        ('docker.workDir', str),
        ('docker.env', list),
    ]
    command = ""
    def __init__(self, args):
        super().__init__(args)
        self.docker = args['docker']
        self.validateEnvVars()
        if not 'workdir' in self.docker.keys():
            self.docker['workDir'] = '/project'

    def validateEnvVars(self):
        if 'env' in self.docker.keys():
            for env_var_index, env_var in enumerate(self.docker['env']):
                if not type(env_var) == str:
                    raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                        self.getId(),
                        f"docker.env[{env_var_index}]",
                        str,
                        type(env_var)
                    ))
        else:
            self.docker['env'] = []

    def execute(self, job_context):
        super().execute(job_context)
        docker.run(
            f"{self.docker['image']}:{self.docker['version']}",
            f"bash -c {self.command}",
            self.docker['workDir'],
            self.docker['env']
        )

class Make(DockerTask):

    required_fields = [
        'target',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.target = args['target']
        self.command = f"make {self.target}"

    def execute(self, job_context):
        super().execute(job_context)

class Shell(DockerTask):

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
