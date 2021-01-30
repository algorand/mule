import boto3
import subprocess
import base64
from shutil import which
import sys

from mule.poc import config
from mule.util import download_util
from mule.util import shell_util

ecr_client = boto3.client('ecr', region_name=config.AWS_REGION)
sts_client = boto3.client('sts', region_name=config.AWS_REGION)
s3_client = boto3.client('s3', region_name=config.AWS_REGION)


def deps():
    if not which('aws'):
        subprocess.run(['pip3', 'install', 'awscli'], check=True)
    if not which('aws-iam-authenticator'):
        if sys.platform == 'darwin':
            subprocess.run(['brew', 'install', 'aws-iam-authenticator'], check=True)
        elif sys.platform == 'linux':
            download_url = "https://amazon-eks.s3.us-west-2.amazonaws.com/1.18.9/2020-11-02/bin/linux/amd64/aws-iam-authenticator"
            download_util.download_to_bin(download_url)


def update_kubeconfig(eks_cluster):
    shell_util.run(['aws', 'eks', 'update-kubeconfig', '--name', eks_cluster, '--region', config.AWS_REGION])


def get_repository(application_name, environment):
    repository_name = f"{application_name}/{environment}"
    return ecr_client.describe_repositories(repositoryNames=[repository_name])['repositories'][0]


def ensure_repository(application_name, environment):
    repository_name = f"{application_name}/{environment}"
    try:
        return get_repository(application_name, environment)
    except ecr_client.exceptions.RepositoryNotFoundException as _:
        return ecr_client.create_repository(
            repositoryName=repository_name,
            imageScanningConfiguration={'scanOnPush': True}
            )['repository']


def ecr_login():
    auth_data = ecr_client.get_authorization_token()['authorizationData'][0]
    auth_info = base64.b64decode(auth_data['authorizationToken']).decode('utf-8').split(':')
    auth_user = auth_info[0]
    auth_pass = auth_info[1]
    auth_url = auth_data['proxyEndpoint']
    shell_util.run(f"docker login -u {auth_user} -p {auth_pass} {auth_url}".split(' '))


def get_aws_account_id():
    caller_identity = sts_client.get_caller_identity()
    return caller_identity['Account']


def get_region():
    return config.AWS_REGION


def ensure_s3_bucket(bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
