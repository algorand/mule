import warnings
import tempfile
from unittest import TestCase

from mule.util import s3_util


class Test(TestCase):

    # ignore resource warning which is due to an open boto3 issue https://github.com/boto/boto3/issues/454
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

    def test__path_leaf(self):
        result = s3_util._path_leaf("test/test2/test3/leaf")
        self.assertEqual(result, 'leaf', "was expecting 'leaf' not '{}'".format(result))

    def test_upload_files(self):
        s3_util.upload_files('resources/test.out', 'algorand-uploads')
        s3_util.upload_files('resources/*.out', 'algorand-uploads')
        s3_util.upload_files(['resources/*.out', 'resources/*.out2'], 'algorand-uploads')

    def test_upload_file(self):
        s3_util.upload_files('resources/test.out', 'algorand-uploads')

    def test_download_file(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            s3_util.download_file("algorand-uploads",
                                  "resources/test.out",
                                  tmpdirname,
                                  "test.out")
            s3_util.download_file("algorand-uploads",
                                  "resources/test.out",
                                  tmpdirname, "test.out")

    def test_download_files(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            s3_util.download_files('algorand-uploads', 'resources', 'out', tmpdirname)
            s3_util.download_files('algorand-uploads', 'resources/test', 'out', tmpdirname)
            s3_util.download_files('algorand-uploads', ['resources/test'], ['out'], tmpdirname)

    def test_list_keys(self):
        s3_util.list_keys('algorand-uploads', ['temp', 'resources'])
        s3_util.list_keys('algorand-uploads', 'resources')

    def test_list_objects(self):
        s3_util.list_objects('algorand-uploads', ['temp', 'resources'])
        s3_util.list_objects('algorand-uploads', 'resources')

    def test_get_matching_s3_objects(self):
        count = 0
        for _ in s3_util.get_matching_s3_objects("algorand-uploads"):
            count += 1
        self.assertTrue(count > 0, "matching object count should be greater than zero")

    def test_get_matching_s3_keys(self):
        count = 0
        for _ in s3_util.get_matching_s3_keys("algorand-uploads"):
            count += 1
        self.assertTrue(count > 0, "matching file key should be greater than zero")
