from mule.task import ITask
import subprocess

class Make(ITask):

    required_fields = [
        'target'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.target = args['target']

    def execute(self, job_context):
        super().execute(job_context)
        make_command = ['make']
        targets_list = self.target.split(' ')
        make_command.extend(targets_list)
        subprocess.run(make_command, check=True)
