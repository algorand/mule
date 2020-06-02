import os
import subprocess
import json
import urllib.request
from mule.util import os_util
from mule.util import file_util
import platform

def install_node(data_dir, bin_dir, channel, installer_version='2.0.4'):
    """
    Download and install algod.
    """
    installer_dir = '/tmp/algod-inst'
    os.makedirs(installer_dir, exist_ok=True)

    os_type = os_util.get_os_type()
    cpu_arch_type = os_util.get_cpu_arch_type()

    installer_url = f"https://algorand-releases.s3.amazonaws.com/channel/stable/install_stable_{os_type}-{cpu_arch_type}_{installer_version}.tar.gz"
    installer_tar_path = f"{installer_dir}/installer.tar.gz"

    _ = urllib.request.urlretrieve(installer_url, installer_tar_path)
    file_util.decompressTarfile(installer_tar_path, f"{installer_dir}")

    installer_command = [f"{installer_dir}/update.sh", '-i', '-n']
    installer_command.extend(['-c', channel])
    installer_command.extend(['-p', bin_dir])
    installer_command.extend(['-d', data_dir])

    subprocess.run(installer_command, check=True)

def configure_node(data_dir, kmd_dir, archival_node=False, algod_port=60000, kmd_port=60001):
    node_configs = {
        'EndpointAddress': f"0.0.0.0:{algod_port}",
        'Archival': archival_node
    }
    kmd_configs = {
        'address': f"0.0.0.0:{kmd_port}"
    }

    file_util.writeJsonFile(f"{data_dir}/config.json", node_configs)
    file_util.writeJsonFile(f"{kmd_dir}/kmd_config.json", kmd_configs)

def start_node(data_dir, kmd_dir, bin_dir=None):
    goal_args = [
        'node',
        'start',
    ]
    goal(data_dir, kmd_dir, goal_args, bin_dir)

def stop_node(data_dir, kmd_dir, bin_dir=None):
    goal_args = [
        'node',
        'stop',
    ]
    goal(data_dir, kmd_dir, goal_args, bin_dir)

def goal(data_dir, kmd_dir, args, bin_dir=None):
    goal_command = ['goal']
    if not bin_dir is None:
        goal_command = [f"{bin_dir}/goal"]

    goal_command.extend([
        '-d', data_dir,
        '-k', kmd_dir,
    ])
    goal_command.extend(args)

    subprocess.run(goal_command, check=True)
