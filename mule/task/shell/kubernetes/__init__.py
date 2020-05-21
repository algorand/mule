from mule.task.shell import IShellTask

class EksCtl(IShellTask):

    required_fields = [
        'action',
        'resource',
        'configPath',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.action = args['action']
        self.resource = args['resource']
        self.configPath = args['configPath']
        self.command = f"eksctl {self.action} {self.resource} -f {self.configPath}".split(' ')

    def execute(self, job_context):
        super().execute(job_context)

class Helm(IShellTask):

    required_fields = [
        'action',
        'opts',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.action = args['action']
        self.opts = args['opts']
        if type(self.opts) == str:
            self.opts = self.opts.split(' ')
        helm_command = ['helm']
        helm_command.append(self.action)
        helm_command.extend(self.opts)
        self.command = helm_command

    def execute(self, job_context):
        super().execute(job_context)
