from mule.task import ITask
from mule.util import algorand_util

class Install(ITask):
    required_fields = [
        'data_dir',
        'bin_dir',
        'channel'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.bin_dir = args['bin_dir']
        self.channel = args['channel']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.install_node(self.data_dir, self.bin_dir, self.channel)

class Configure(ITask):
    required_fields = [
        'data_dir',
        'kmd_dir',
    ]
    algod_port = 60000
    kmd_port = 60001
    archival_node = False

    def __init__(self, args):
        super().__init__(args)
        self.data_dir = args['data_dir']
        self.kmd_dir = args['kmd_dir']
        if 'algod_port' in args:
            self.algod_port = args['algod_port']
        if 'kmd_port' in args:
            self.kmd_port = args['kmd_port']
        if 'archival_node' in args:
            self.archival_node = args['archival_node']

    def execute(self, job_context):
        super().execute(job_context)
        algorand_util.configure_node(
            self.data_dir,
            self.kmd_dir,
            self.archival_node,
            self.algod_port,
            self.kmd_port
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
