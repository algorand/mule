from mule.task import ITask
import subprocess

class IShellTask(ITask):
    required_fields = [
        'command'
    ]

    def execute(self, job_context):
        super().execute(job_context)
        subprocess.run(self.command, check=True)

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
