from mule.task import ITask
from mule.util import s3_util
from mule.util import time_util
from mule.util import file_util
from mule.error import messages

class Stash(ITask):
    required_fields = [
        'bucketName',
        'stashId',
        'globSpecs'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.globSpecs = args['globSpecs']
        self.bucketName = args['bucketName']
        self.stashId = args['stashId']
        if not type(self.stashId) == str or len(self.stashId) == 0:
            raise Exception(messages.STASH_ID_EXCEPTION.format(self.getId()))

    def stash(self):
        file_name = f"stash-{time_util.get_timestamp()}.tar.gz"
        file_util.compressFiles(file_name, self.globSpecs)
        s3_util.upload_file(file_name, self.bucketName, f"{self.stashId}/stash.tar.gz")
        file_util.deleteFile(file_name)

    def execute(self, job_context):
        super().execute(job_context)
        self.stash()

class Unstash(ITask):
    required_fields = [
        'bucketName',
        'stashId',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.bucketName = args['bucketName']
        self.stashId = args['stashId']

    def unstash(self):
        file_name = f"stash-{time_util.get_timestamp()}.tar.gz"
        s3_util.download_file(self.bucketName, f"{self.stashId}/stash.tar.gz", '.', file_name)
        file_util.decompressTarfile(file_name)
        file_util.deleteFile(file_name)

    def execute(self, job_context):
        super().execute(job_context)
        self.unstash()
