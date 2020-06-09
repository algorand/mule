import logging
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import ClientError
import ntpath
import os.path
import glob
import os

def get_s3_client(auth=True):
    if not auth:
        return boto3.client('s3', config=Config(signature_version=UNSIGNED))
    return boto3.client('s3')

def _path_leaf(path: str) -> str:
    """
    Return the leaf object of the given path.
    :param path: directory path to parse
    :return: leaf object of path
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def _get_object_name(file: str, preserveDirs: bool) -> str:
    if preserveDirs:
        return file.replace('./', '')

    return os.path.basename(file)

def upload_files(globspec: object, bucket_name: str, prefix = None, preserveDirs = False) -> bool:
    """
    Upload files using a list of globs to an S3 bucket.
    :param globspec: Glob to match local files
    :param bucket_name: Bucket name to upload to.
    :param prefix: Upload objects whose key starts with this prefix (optional).
    :param preserveDirs: Preserve the local directory structure of the file(s) location on the server (optional).
    :return: True if successful, otherwise False.
    """
    response = True
    if isinstance(globspec, str):
        globspecs = (globspec,)
    else:
        globspecs = globspec
    for globspec in globspecs:
        files = glob.glob(globspec, recursive=True)
        for file in files:
            if os.path.isfile(file):
                object_name = _get_object_name(file, preserveDirs)
                if prefix != None:
                    # Remove both "./" from the beginning and "/" from both sides, if present.
                    object_name = f"{prefix.lstrip('.').strip('/')}/{object_name}"
                response &= upload_file(file, bucket_name, object_name)
    return response


def upload_file(file_name: str, bucket_name: str, object_name=None, preserveDirs = False) -> bool:
    """
    Upload a file to an S3 bucket
    :param file_name: File path to upload.
    :param bucket_name: S3 bucket name to upload to.
    :param object_name: Object name (key).
    :param preserveDirs: Preserve the local directory structure of the file(s) location on the server (optional).
    :return: True if successful, otherwise False.
    """
    try:
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = _get_object_name(file_name, preserveDirs)
        s3_client = get_s3_client()
        # Upload the file
        print("uploading file '{}' to bucket '{}' to object '{}'".format(file_name, bucket_name, object_name))
        response = s3_client.upload_file(file_name, bucket_name, object_name)
        if response is not None:
            print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file(bucket_name: str, object_name: str, output_dir: str = ".", file_name: str = None, s3_auth = True) -> bool:
    """
    Download a file from an S3 bucket.
    :param bucket_name: Name of the S3 bucket.
    :param object_name: Name of object (key).
    :param output_dir: Directory where to place the files (optional). If not specified, use current directory.
    :param file_name: Name of output file (optional). If not specified, use the key leaf.
    :return: True if successful, otherwise False.
    """
    try:
        if file_name is None:
            file_path = os.path.join(output_dir, _path_leaf(object_name))
        else:
            file_path = os.path.join(output_dir, file_name)
        print("downloading object '{}' from bucket '{}' to file '{}'".format(object_name, bucket_name, file_path))
        s3_client = get_s3_client(s3_auth)
        response = s3_client.download_file(bucket_name, object_name, file_path)
        if response is not None:
            print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_files(bucket_name: str, prefix: object = "", suffix: object = "", output_dir: str = ".", s3_auth = True) -> bool:
    """
    Download Files from S3 bucket.
    :param bucket_name: Name of the S3 bucket.
    :param prefix: Download objects whose key starts with this prefix (optional).
    :param suffix: Download objects whose keys end with this suffix (optional).
    :param output_dir: Directory where to place the files (optional). If not specified, use current directory.
    :return: True if successful, otherwise False.
    """
    result = True
    for key in get_matching_s3_keys(bucket_name, prefix, suffix, s3_auth=s3_auth):
        result &= download_file(bucket_name, key, output_dir, s3_auth=s3_auth)
    return result


def get_bucket_keys(bucket_name: str, prefix: object = "", suffix: object = "", s3_auth = True):
    objects = get_s3_client(s3_auth).list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [ obj['Key'] for obj in objects['Contents'] ]


def copy_bucket_object(source_bucket: str, source_key: str, dest_bucket: str, dest_key: str):
    s3_client = boto3.resource('s3')
    copy_source = {
        'Bucket': source_bucket,
        'Key'   : source_key
    }

    filename = source_key.split('/')[-1]
    s3_client.meta.client.copy(copy_source, dest_bucket, dest_key + '/' + filename)


def list_keys(bucket_name: str, prefix: object = "", suffix: object = "", s3_auth = True):
    """
    Print keys in S3 bucket.
    :param bucket_name: Name of the S3 bucket.
    :param prefix: List keys whose key starts with this prefix (optional).
    :param suffix: List keys whose keys end with this suffix (optional).
    """
    for key in get_matching_s3_keys(bucket_name, prefix, suffix, s3_auth=s3_auth):
        print(key)


def list_objects(bucket_name: str, prefix: object = "", suffix: object = "", s3_auth = True):
    """
    Print objects in S3 bucket.
    :param bucket_name: Name of the S3 bucket.
    :param prefix: List objects whose key starts with this prefix (optional).
    :param suffix: List objects whose keys end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket_name, prefix, suffix, s3_auth=s3_auth):
        print(obj)


# based on https://alexwlchan.net/2019/07/listing-s3-keys/
def get_matching_s3_objects(bucket: str, prefix: object = "", suffix: object = "", s3_auth = True):
    """
    Generate objects in an S3 bucket.
    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional).
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    """
    s3 = get_s3_client(s3_auth)
    paginator = s3.get_paginator("list_objects_v2")

    kwargs = {'Bucket': bucket}

    # We can pass the prefix directly to the S3 API.  If the user has passed
    # a tuple or list of prefixes, we go through them one by one.
    if isinstance(prefix, str):
        prefixes = (prefix,)
    else:
        prefixes = prefix

    if isinstance(suffix, str):
        suffixes = (suffix,)
    else:
        suffixes = suffix

    for key_prefix in prefixes:
        kwargs["Prefix"] = key_prefix

        for page in paginator.paginate(**kwargs):
            try:
                contents = page["Contents"]
            except KeyError:
                break

            for obj in contents:
                key = obj["Key"]
                if key.endswith(tuple(suffixes)):
                    yield obj


def get_matching_s3_keys(bucket: str, prefix: object = "", suffix: object = "", s3_auth = True):
    """
    Generate the keys in an S3 bucket.
    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket, prefix, suffix, s3_auth=s3_auth):
        yield obj["Key"]
