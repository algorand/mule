import os
import tempfile
import warnings
from unittest import TestCase
from mule.task.s3 import ListFiles, DownloadFile, UploadFile, UploadFiles
from mule.util import JobContext


class TestArchiveTasks(TestCase):

    # ignore resource warning which is due to an open boto3 issue https://github.com/boto/boto3/issues/454
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

    def test_list_files(self):
        s3_list_file_task1 = ListFiles({
            'bucketName': 'algorand-releases', 'suffix': 'sig'
        })
        s3_list_file_task1.execute(JobContext())
        s3_list_file_task2 = ListFiles({
            'bucketName': 'algorand-builds', 'prefix': 'channel/beta'
        })
        s3_list_file_task2.execute(JobContext())

    def test_download_file(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            s3_download_file_task1 = DownloadFile({
                'bucketName': 'algorand-releases',
                'objectName': 'install/offline_install_stable_darwin-amd64.tar.gz.sig',
                'outputDir': tmpdirname
            })
            s3_download_file_task1.execute(JobContext())
            self.assertEqual(len(os.listdir(tmpdirname)), 1, "expected file count of 1")

    def test_upload_file(self):
        s3_upload_file_task1 = UploadFile({
            'bucketName': 'algorand-uploads',
            'fileName': 'resources/test.out'
        })
        s3_upload_file_task1.execute(JobContext())

    def test_upload_files(self):
        s3_upload_files_task1 = UploadFiles({
            'bucketName': 'algorand-uploads',
            'globSpec': 'resources/*.out'
        })
        s3_upload_files_task1.execute(JobContext())
        s3_upload_files_task2 = UploadFiles({
            'bucketName': 'algorand-uploads',
            'globSpec': ['resources/*.out', 'resources/*.out2']
        })
        s3_upload_files_task2.execute(JobContext())
