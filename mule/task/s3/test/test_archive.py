from unittest import TestCase
from mule.task.s3.archive import ListFiles


class TestListFiles(TestCase):
    def test_list_files(self):
        s3ListFileTask = ListFiles('algorand-releases')
        s3ListFileTask.execute(s3ListFileTask)
