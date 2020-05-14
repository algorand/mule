import logging
import boto3
from botocore.exceptions import ClientError
import ntpath
import os.path
import glob
import os


def _path_leaf(path: str) -> str:
    """
    Return the leaf object of the given path.
    :param path: directory path to parse
    :return: leaf object of path
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def upload_files(globspec: object, bucket_name: str, prefix = None) -> bool:
    """
    Upload files using a list of globs to an S3 bucket.
    :param globspec: Glob to match local files
    :param bucket_name: Bucket name to upload to.
    :param prefix: Prefix for object names placed in s3
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
                file = file.replace('./', '')
                object_name = file
                if prefix != None:
                    object_name = f"{prefix}{file}"
                response &= upload_file(file, bucket_name, object_name)
    return response


def upload_file(file_name: str, bucket_name: str, object_name=None) -> bool:
    """
    Upload a file to an S3 bucket
    :param file_name: File path to upload.
    :param bucket_name: S3 bucket name to upload to.
    :param object_name: Object name (key).
    :return: True if successful, otherwise False.
    """
    try:
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name
        print("uploading file '{}' to bucket '{}' to object '{}'".format(file_name, bucket_name, object_name))
        s3_client = boto3.client('s3')
        # Upload the file
        response = s3_client.upload_file(file_name, bucket_name, object_name)
        if response is not None:
            print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file(bucket_name: str, object_name: str, output_dir: str = ".", file_name: str = None) -> bool:
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
        s3_client = boto3.client('s3')
        response = s3_client.download_file(bucket_name, object_name, file_path)
        if response is not None:
            print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_files(bucket_name: str, prefix: object = "", suffix: object = "", output_dir: str = ".") -> bool:
    """
    Download Files from S3 bucket.
    :param bucket_name: Name of the S3 bucket.
    :param prefix: Download objects whose key starts with this prefix (optional).
    :param suffix: Download objects whose keys end with this suffix (optional).
    :param output_dir: Directory where to place the files (optional). If not specified, use current directory.
    :return: True if successful, otherwise False.
    """
    result = True
    for key in get_matching_s3_keys(bucket_name, prefix, suffix):
        result &= download_file(bucket_name, key, output_dir)
    return result


def list_keys(bucket_name: str, prefix: object = "", suffix: object = ""):
    """
    Print keys in S3 bucket.
    :param bucket_name: Name of the S3 bucket.
    :param prefix: List keys whose key starts with this prefix (optional).
    :param suffix: List keys whose keys end with this suffix (optional).
    """
    for keys in get_matching_s3_keys(bucket_name, prefix, suffix):
        print(keys)


def list_objects(bucket_name: str, prefix: object = "", suffix: object = ""):
    """
    Print objects in S3 bucket.
    :param bucket_name: Name of the S3 bucket.
    :param prefix: List objects whose key starts with this prefix (optional).
    :param suffix: List objects whose keys end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket_name, prefix, suffix):
        print(obj)


# based on https://alexwlchan.net/2019/07/listing-s3-keys/
def get_matching_s3_objects(bucket: str, prefix: object = "", suffix: object = ""):
    """
    Generate objects in an S3 bucket.
    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional).
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    """
    s3 = boto3.client("s3")
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


def get_matching_s3_keys(bucket: str, prefix: object = "", suffix: object = ""):
    """
    Generate the keys in an S3 bucket.
    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        yield obj["Key"]
