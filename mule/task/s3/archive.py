from mule.task import ITask
from mule.util import s3_util


class Upload(ITask):
    required_fields = [
        'bucketName',
        'fileName'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.bucketName = args['bucketName']
        self.fileName = args['fileName']
        if 'objectName' in args:
            self.objectName = args['objectName']

    def upload_file(self):
        s3_util.upload_file(self.fileName, self.bucketName, self.objectName)

    def execute(self, job_context):
        super().execute(job_context)
        self.upload_file()


class Download(ITask):
    required_fields = [
        'bucketName',
        'objectName'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.bucketName = args['bucketName']
        self.objectName = args['objectName']
        if 'outputDir' in args:
            self.outputDir = args['outputDir']
        if 'fileName' in args:
            self.fileName = args['fileName']

    def download_file(self):
        s3_util.download_file(self.bucketName, self.objectName, self.outputDir, self.fileName)

    def execute(self, job_context):
        super().execute(job_context)
        self.download_file()


class ListFiles(ITask):
    required_fields = [
        'bucketName'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.bucketName = args['bucketName']
        if 'prefix' in args:
            self.prefix = args['prefix']
        if 'suffix' in args:
            self.suffix = args['suffix']

    def list_files(self):
        s3_util.list_keys(self.bucketName, self.prefix, self.suffix)

    def execute(self, job_context):
        super().execute(job_context)
        self.list_files()
