from mule.task import ITask
import subprocess

class Shell(ITask):
    required_fields = [
        'command'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.command = args['command']
        if type(self.command) == str:
            self.command = self.command.split(' ')

    def execute(self, job_context):
        super().execute(job_context)
        subprocess.run(self.command, check=True)


class Make(ITask):
    required_fields = [
        'target',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.target = args['target']

    def execute(self, job_context):
        super().execute(job_context)
        subprocess.run(f"make {self.target}".split(' '), check=True)


