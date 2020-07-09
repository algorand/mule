from mule.task import ITask
import subprocess

class IShellTask(ITask):
    def execute(self, job_context):
        super().execute(job_context)
        subprocess.run(self.command, check=True)


class Shell(IShellTask):
    required_fields = [
        'command'
    ]

    save_logs = False

    def __init__(self, args):
        super().__init__(args)
        self.command = args['command']
        if type(self.command) == str:
            self.command = self.command.split(' ')
        if 'saveLogs' in args:
            self.save_logs = args['saveLogs']

    def execute(self, job_context):
        if self.save_logs:
            print(f"running sub process {self.command}")
            command_logs = subprocess.run(self.command, capture_output=True, check=True)
            return {
                'stdout': command_logs.stdout.decode('utf-8').rstrip("\n"),
                'stderr': command_logs.stderr.decode('utf-8').rstrip("\n"),
                'returncode': command_logs.returncode
            }
        else:
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


