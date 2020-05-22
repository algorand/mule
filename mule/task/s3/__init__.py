import re

from mule.task import ITask
from mule.util import s3_util


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
    prefix = None

    def __init__(self, args):
        super().__init__(args)
        self.globSpec = args['globSpec']
        self.bucketName = args['bucketName']
        if 'prefix' in args:
            self.prefix = args['prefix']

    def upload_file(self):
        s3_util.upload_files(self.globSpec, self.bucketName, self.prefix)

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
        self.suffix = args['suffix'] if 'suffix' in args else ''
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


class BucketCopy(ITask):
    required_fields = [
        'src',
        'dest'
    ]

    # https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
    bucketRe = re.compile(r'^(s3://)?([a-z0-9-.]*)\/?(.*)?$')

    def __init__(self, args):
        super().__init__(args)
        self.src = args['src']
        self.dest = args['dest']

    def copy(self):
        src_s3, src_bucket, src_prefix = self.bucketRe.findall(self.src)[0]
        dest_s3, dest_bucket, dest_prefix = self.bucketRe.findall(self.dest)[0]

        if src_s3 and dest_s3:
            for src_key in s3_util.get_bucket_keys(src_bucket, src_prefix):
                s3_util.copy_bucket_object(src_bucket, src_key, dest_bucket, dest_prefix)
        elif src_s3 or dest_s3:
            if src_s3:
                # Downloading s3 -> local.
                prefix = src_prefix
                suffix = ''
                if src_prefix[-1] != '/':
                    rightmost_idx = src_prefix.rfind('/')
                    prefix = src_prefix[:rightmost_idx]
                    filename_and_ext = src_prefix[rightmost_idx:]
                    # "+1" to not include the backslash char.
                    suffix = filename_and_ext[filename_and_ext.rfind('.') + 1:]

                # To get the glob, join the last two tuple elements, i.e., ('', 'bar, 'foo') => 'bar/foo'
                s3_util.download_files(src_bucket, prefix, suffix, '/'.join((dest_bucket, dest_prefix)))
            else:
                # Uploading local -> s3.
                # To get the glob, join the last two tuple elements, i.e., ('', 'bar, '*.out') => 'bar/*.out'
                s3_util.upload_files('/'.join((src_bucket, src_prefix)), dest_bucket, dest_prefix)
        else:
            # TODO: raise exception, both can't be local.
            pass

    def execute(self, job_context):
        super().execute(job_context)
        self.copy()


