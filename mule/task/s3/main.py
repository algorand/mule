from mule.task import ITask
from mule.util import s3_util

class Test(ITask):
    name = 'test'
    dependencies = [],
    required_fields = [
        'bucketName'
    ]

    def __init__(self, args):
#        super().__init__({
#            'name': self.name,
#            'dependencies': self.dependencies,
#            'required_fields': self.required_fields + args['required_fields'] if 'required_fields' in args else self.required_fields
#        })
        super().__init__(args)
        print('got here')
        print(self.ctx['required_fields'])

t = Test({
    'required_fields': [
        'globSpec',
        'fileName'
    ]
})

class S3(ITask):
#    required_fields = [
#        'bucketName',
#    ]

    def __init__(self, args):
        required_fields = args['required_fields']

        super().__init__(args)
        self.fileName = args['fileName']
        self.bucketName = args['bucketName']
        self.objectName = args['objectName'] if 'objectName' in args else None

    def upload_file(self):
        s3_util.upload_file(self.fileName, self.bucketName, self.objectName)

    def upload_files(self):
        s3_util.upload_files(self.globSpec, self.bucketName)

    def download_file(self):
        s3_util.download_file(self.bucketName, self.objectName, self.outputDir, self.fileName)

    def download_files(self):
        s3_util.download_files(self.bucketName, self.prefix, self.suffix, self.outputDir)

    def list_files(self):
        s3_util.list_keys(self.bucketName, self.prefix, self.suffix)

    def execute(self, job_context):
        super().execute(job_context)
        self.upload_file()


class UploadFile(ITask):
    required_fields = [
        'bucketName',
        'fileName'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.fileName = args['fileName']
        self.bucketName = args['bucketName']
        self.objectName = args['objectName'] if 'objectName' in args else None

    def upload_file(self):
        s3_util.upload_file(self.fileName, self.bucketName, self.objectName)

    def execute(self, job_context):
        super().execute(job_context)
        self.upload_file()


class UploadFiles(ITask):
    required_fields = [
        'bucketName',
        'globSpec'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.globSpec = args['globSpec']
        self.bucketName = args['bucketName']

    def upload_file(self):
        s3_util.upload_files(self.globSpec, self.bucketName)

    def execute(self, job_context):
        super().execute(job_context)
        self.upload_file()


class DownloadFile(ITask):
    required_fields = [
        'bucketName',
        'objectName'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.bucketName = args['bucketName']
        self.objectName = args['objectName']
        self.outputDir = args['outputDir'] if 'outputDir' in args else '.'
        self.fileName = args['fileName'] if 'fileName' in args else None

    def download_file(self):
        s3_util.download_file(self.bucketName, self.objectName, self.outputDir, self.fileName)

    def execute(self, job_context):
        super().execute(job_context)
        self.download_file()


class DownloadFiles(ITask):
    required_fields = [
        'bucketName',
        'prefix'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.bucketName = args['bucketName']
        self.prefix = args['prefix']
        self.suffix = args['suffix'] if 'suffix' in args else None
        self.outputDir = args['outputDir'] if 'outputDir' in args else '.'

    def download_files(self):
        s3_util.download_files(self.bucketName, self.prefix, self.suffix, self.outputDir)

    def execute(self, job_context):
        super().execute(job_context)
        self.download_files()


class ListFiles(ITask):
    required_fields = [
        'bucketName'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.bucketName = args['bucketName']
        self.prefix = args['prefix'] if 'prefix' in args else ''
        self.suffix = args['suffix'] if 'suffix' in args else ''

    def list_files(self):
        s3_util.list_keys(self.bucketName, self.prefix, self.suffix)

    def execute(self, job_context):
        super().execute(job_context)
        self.list_files()

