from mule.task import ITask
from mule.util import algorand_util

class Install(ITask):
    required_fields = [
        'data_dir',
        'bin_dir',
        'channel'
    ]
    version = 'latest'

    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.bin_dir = args['bin_dir']
        self.channel = args['channel']

        if 'version' in args:
            self.version = args['version']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.install_node(self.data_dir, self.bin_dir, self.channel, self.version)

class Configure(ITask):
    required_fields = [
        'data_dir',
        'kmd_dir',
    ]
    node_configs = {}
    kmd_configs = {}
    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.kmd_dir = args['kmd_dir']
        if 'node_configs' in args:
            self.node_configs = args['node_configs']
        if 'kmd_configs' in args:
            self.kmd_configs = args['kmd_configs']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.configure_node(
            self.data_dir,
            self.kmd_dir,
            self.node_configs,
            self.kmd_configs
        )

class ShowConfigs(ITask):
    required_fields = [
        'data_dir',
        'kmd_dir',
    ]
    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.kmd_dir = args['kmd_dir']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.show_node_configs(
            self.data_dir,
            self.kmd_dir
        )

class Start(ITask):
    required_fields = [
        'data_dir',
        'kmd_dir',
    ]
    bin_dir = None

    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.kmd_dir = args['kmd_dir']
        if 'bin_dir' in args:
            self.bin_dir = args['bin_dir']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.start_node(self.data_dir,  self.kmd_dir, self.bin_dir)

class Restart(ITask):
    required_fields = [
        'data_dir',
        'kmd_dir',
    ]
    bin_dir = None

    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.kmd_dir = args['kmd_dir']
        if 'bin_dir' in args:
            self.bin_dir = args['bin_dir']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.restart_node(self.data_dir,  self.kmd_dir, self.bin_dir)

class Status(ITask):
    required_fields = [
        'data_dir',
        'kmd_dir',
    ]
    bin_dir = None

    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.kmd_dir = args['kmd_dir']
        if 'bin_dir' in args:
            self.bin_dir = args['bin_dir']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.status_node(self.data_dir,  self.kmd_dir, self.bin_dir)

class Stop(ITask):
    required_fields = [
        'data_dir',
        'kmd_dir',
    ]
    bin_dir = None

    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.kmd_dir = args['kmd_dir']
        if 'bin_dir' in args:
            self.bin_dir = args['bin_dir']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.stop_node(self.data_dir,  self.kmd_dir, self.bin_dir)
