from mule.task import ITask
import mule.util.docker_util as docker

class Build(ITask):

    required_fields = [
        'buildContextPath',
        'tags',
        'dockerFilePath'
    ]
    buildArgs = ''

    def __init__(self, args):
        super().__init__(args)
        self.buildContextPath = args['buildContextPath']
        self.tags = args['tags']
        self.dockerFilePath = args['dockerFilePath']

        if 'buildArgs' in args:
            self.buildArgs = args['buildArgs']

    def execute(self, job_context):
        super().execute(job_context)
        print('Building docker image')
        docker.build(self.buildArgs, self.buildContextPath, self.tags, self.dockerFilePath)

class Ensure(ITask):

    required_fields = [
        'version',
        'image',
        'dockerFilePath',
        'arch',
    ]
    buildContextPath= "."

    def __init__(self, args):
        super().__init__(args)
        self.arch = args['arch']
        self.image = args['image']
        self.version = args['version']
        self.dockerFilePath = args['dockerFilePath']
        if 'buildContextPath' in args:
            self.buildContextPath = args['buildContextPath']

    def execute(self, job_context):
        super().execute(job_context)
        print('Checking to see if docker image is available')
        docker.ensure(f"{self.image}:{self.version}", self.arch, self.buildContextPath, self.dockerFilePath)
