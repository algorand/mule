from mule.task import ITask
from mule.util import algorand_util
from mule.validator import validateRequiredTaskFieldsPresent

class Start(ITask):
    required_fields = [
        'node',
        'postgres',
    ]
    node = {}
    postgres = {}

    bin_dir = None
    pid_file = None
    log_file_name = None

    def __init__(self, args):
        super().__init__(args)
        self.validate_fields(args)
        self.node.update(args['node'])
        self.postgres.update(args['postgres'])
        if 'bin_dir' in args:
            self.bin_dir = args['bin_dir']
        if 'pid_file' in args:
            self.pid_file = args['pid_file']
        if 'log_file_name' in args:
            self.log_file_name = args['log_file_name']
    
    def validate_fields(self, args):
        self.validate_node_fields(args['node'])
        self.validate_postgres_fields(args['postgres'])

    def validate_node_fields(self, node):
        remote_node_fields = ['host', 'port', 'token', 'genesis']
        local_node_fields = ['data']
        contains_remote_node_fields = all(field in node for field in remote_node_fields)
        contains_local_node_fields = all(field in node for field in local_node_fields)
        if not contains_remote_node_fields and not contains_local_node_fields:
            if not contains_remote_node_fields:
                validateRequiredTaskFieldsPresent(
                    self.task_id,
                    node,
                    remote_node_fields
                )
            else:
                validateRequiredTaskFieldsPresent(
                    self.task_id,
                    node,
                    local_node_fields
                )

    def validate_postgres_fields(self, postgres):
        postgres_fields = ['host', 'port', 'user', 'password']
        validateRequiredTaskFieldsPresent(
            self.task_id,
            postgres,
            postgres_fields
        )

    def execute(self, job_context):
        super().execute(job_context)
        if 'data' in self.node:
            algorand_util.start_indexer_local_node(self.node, self.postgres, self.bin_dir, self.pid_file, self.log_file_name)
        else:
            algorand_util.start_indexer_remote_node(self.node, self.postgres, self.bin_dir, self.pid_file, self.log_file_name)
