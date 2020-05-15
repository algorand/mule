from mule.task import ITask
from mule.util import s3_util
from mule.util import time_util
from mule.util.file_util import compressFiles

class Stash(ITask):
    required_fields = [
        'bucketName',
        'stash_id',
        'globSpec'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.globSpec = args['globSpec']
        self.bucketName = args['bucketName']
        self.stash_id = args['stash_id']

    def upload_file(self):
        file_name = f"stash-{time_util.get_timestamp()}.tar.gz"
        compressFiles(file_name, self.globSpec)
        s3_util.upload_file(file_name, self.bucketName, f"{self.stash_id}/stash.tar.gz")

    def execute(self, job_context):
        super().execute(job_context)
        self.upload_file()
