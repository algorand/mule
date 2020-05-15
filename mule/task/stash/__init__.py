from mule.task import ITask
from mule.util import s3_util
from mule.util import time_util
from mule.util import file_util

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

    def stash(self):
        file_name = f"stash-{time_util.get_timestamp()}.tar.gz"
        file_util.compressFiles(file_name, self.globSpec)
        s3_util.upload_file(file_name, self.bucketName, f"{self.stash_id}/stash.tar.gz")
        file_util.deleteFile(file_name)

    def execute(self, job_context):
        super().execute(job_context)
        self.stash()

class Unstash(ITask):
    required_fields = [
        'bucketName',
        'stash_id',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.bucketName = args['bucketName']
        self.stash_id = args['stash_id']

    def unstash(self):
        file_name = f"stash-{time_util.get_timestamp()}.tar.gz"
        s3_util.download_file(self.bucketName, f"{self.stash_id}/stash.tar.gz", '.', file_name)
        file_util.decompressTarfile(file_name)
        file_util.deleteFile(file_name)

    def execute(self, job_context):
        super().execute(job_context)
        self.unstash()
