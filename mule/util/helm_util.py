import subprocess

from mule.ci import config
from mule.util import aws_util, download_util, file_util
from shutil import which
import sys

from mule.util import shell_util


def deps():
    if not which('helm'):
        if sys.platform == 'darwin':
            subprocess.run(['brew', 'install', 'helm'], check=True)
        if sys.platform == 'linux':
            download_url = "https://get.helm.sh/helm-v3.5.0-linux-amd64.tar.gz"
            with download_util.download_to_tmp(download_url) as (path, folder):
                file_util.untar_file(path)
                file_util.add_to_bin(f"{folder}/linux-amd64/helm")


def deploy(application_name, environment, version, chart):
    repository = aws_util.get_repository(application_name, environment)
    repository_uri = repository['repositoryUri']
    opts = [
        '--install',
        '-n', environment,
        '--create-namespace',
        '--set', f"deployment.image={repository_uri}",
        '--set', f"deployment.version={version}",
        '--set', f"environment={environment}",
    ]

    if file_util.is_file(config.MULE_FILE_PATH):
        opts.extend(['-f', config.MULE_FILE_PATH])

    opts.extend([application_name, chart])
    helm('upgrade', opts)


def delete(application_name, environment):
    helm('delete', [
        '-n', environment,
        application_name,
    ])


def update_repo():
    helm('repo', ['update'])


def helm(action, opts=[]):
    command = ['helm', action]
    command.extend(opts)
    shell_util.run(command, check=True)
