import shutil

import wget
import tempfile
import os
from contextlib import contextmanager

from mule.ci import config
from mule.util import file_util


def download_to_bin(url):
    path = wget.download(url, config.EKS_CLUSTER_NAME)
    file_util.make_executable(path)


def download_to_dir(url, dir):
    os.mkdir(dir)
    return wget.download(url, dir)


@contextmanager
def download_to_tmp(url):
    tfile = tempfile.mkdtemp()
    try:
        yield wget.download(url, tfile), tfile
    finally:
        shutil.rmtree(tfile)
