import re
import os
import pathlib

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
        self.preserveDirs = args['preserveDirs'] if 'preserveDirs' in args else False

    def upload_file(self):
        s3_util.upload_file(self.fileName, self.bucketName, self.objectName, self.preserveDirs)

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
        self.preserveDirs = args['preserveDirs'] if 'preserveDirs' in args else False
        self.prefix = args['prefix'] if 'prefix' in args else None

    def upload_file(self):
        s3_util.upload_files(self.globSpec, self.bucketName, self.prefix, self.preserveDirs)

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
        src_is_remote, src_bucket, src_prefix = self.bucketRe.findall(self.src)[0]
        dest_is_remote, dest_bucket, dest_prefix = self.bucketRe.findall(self.dest)[0]

        if src_is_remote and dest_is_remote:
            for src_key in s3_util.get_bucket_keys(src_bucket, src_prefix):
                s3_util.copy_bucket_object(src_bucket, src_key, dest_bucket, dest_prefix)
        elif src_is_remote or dest_is_remote:
            if src_is_remote:
                # Downloading s3 -> local.

                prefix = src_prefix
                suffix = ''

                # Currently, we can't just do a file check since we're supporting wildcards such as:
                #
                #       s3://my_bucket/foo/bar/*.out
                #
                if src_prefix[-1] != '/':
                    path = pathlib.Path(prefix)
                    # We need to check for suffixes here, i.e. .tar.gz, which would return [.tar, .gz].
                    # If we just check for extension, we'll only get .gz, which may not be what we want.
                    suffix = "".join(path.suffixes) if len(path.suffixes) else ''

                    # The current download_files function does not support wildcards, so we need to futz a bit
                    # to get the expected behavior.
                    #
                    # The value of `suffix` begins with a period, so in order to determine if a wildcard had
                    # been given as the filename we need to instead inspect `path.name`, which will be the
                    # full file name, i.e., `1.out` or `*.out`.
                    #
                    # For the latter, the easiest way to get the expected prefix is to use our old friend
                    # os.path.dirname.
                    if len(suffix) and path.name[0] == '*':
                        prefix = os.path.dirname(src_prefix)

                # To get the wildcard, join the last two tuple elements, i.e., ('', 'bar, 'foo') => 'bar/foo'
                s3_util.download_files(src_bucket, prefix, suffix, '/'.join((dest_bucket, dest_prefix)))
            else:
                # Uploading local -> s3.
                if os.path.isdir(self.src):
                    # This will handle all cases correctly:
                    # 1. foo -> foo/*
                    # 2. foo/ -> foo/*
                    # 3. foo/* -> foo/*
                    src_prefix = src_prefix.rstrip('*').rstrip('/') + '/*'

                # To get the wildcard, join the last two tuple elements, i.e., ('', 'bar, '*.out') => 'bar/*.out'
                s3_util.upload_files('/'.join((src_bucket, src_prefix)), dest_bucket, dest_prefix)
        else:
            raise ValueError('src and dest configs cannot both be local')

    def execute(self, job_context):
        super().execute(job_context)
        self.copy()


