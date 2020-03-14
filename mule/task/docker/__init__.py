from mule.task import ITask
import mule.util.docker_util as docker

class Make(ITask):

    required_fields = [
        'image',
        'version',
        'target',
    ]

    workDir = '/project'

    def __init__(self, args):
        super().__init__(args)
        self.image = args['image']
        self.version = args['version']
        self.target = args['target']

        if 'workDir' in args:
            self.workDir = args['workDir']

    def execute(self, job_context):
        super().execute(job_context)
        docker.run(f"{self.image}:{self.version}", f"make {self.target}", self.workDir)

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

class Shell(ITask):

    required_fields = [
        'image',
        'version',
        'command',
    ]

    workDir = '/project'

    def __init__(self, args):
        super().__init__(args)
        self.image = args['image']
        self.version = args['version']
        self.command = args['command']

        if 'workDir' in args:
            self.workDir = args['workDir']

    def execute(self, job_context):
        super().execute(job_context)
        docker.run(f"{self.image}:{self.version}", self.command, self.workDir)
