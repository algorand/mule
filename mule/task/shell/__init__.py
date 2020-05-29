from mule.task import ITask
import subprocess

class IShellTask(ITask):

    command = []
    def execute(self, job_context):
        super().execute(job_context)
        if type(self.command) == str:
            self.command = self.command.split(' ')
        subprocess.run(self.command, check=True)

class Shell(IShellTask):

    required_fields = [
        'command'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.command = args['command']

    def execute(self, job_context):
        super().execute(job_context)

class Make(IShellTask):

    required_fields = [
        'target',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.target = args['target']
        self.command = f"make {self.target}".split(' ')

    def execute(self, job_context):
        super().execute(job_context)
