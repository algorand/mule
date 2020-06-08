import os
import subprocess
import json
import urllib.request
from mule.util import os_util
from mule.util import file_util
from mule.util import time_util
from mule.util import s3_util
from mule.util import semver_util
import platform

def build_algo_release_url(package_type, channel, os_type, cpu_arch_type, package_version):
    return f"https://algorand-releases.s3.amazonaws.com/channel/{channel}/{package_type}_{channel}_{os_type}-{cpu_arch_type}_{package_version}.tar.gz"

def get_latest_package_version(package_type, channel, os_type, cpu_arch_type):
    os_type = os_util.get_os_type()
    cpu_arch_type = os_util.get_cpu_arch_type()
    package_keys = s3_util.list_keys(
        'algorand-releases',
        f"channel/{channel}/{package_type}_{channel}_{os_type}-{cpu_arch_type}_",
        'tar.gz'
    )
    package_versions = list(map(semver_util.parse_version, package_keys))
    return semver_util.get_highest_version(package_versions)

def install_node(data_dir, bin_dir, channel, node_package_version='latest'):
    """
    Download and install algod.
    """
    node_package_dir = file_util.ensure_folder(f"/tmp/algod-pkg-{time_util.get_timestamp()}")
    data_dir = file_util.ensure_folder(data_dir)
    bin_dir = file_util.ensure_folder(bin_dir)

    os_type = os_util.get_os_type()
    cpu_arch_type = os_util.get_cpu_arch_type()

    if node_package_version == 'latest':
        if channel == 'test':
            node_package_version = get_latest_package_version('node', 'stable', os_type, cpu_arch_type)
        else:
            node_package_version = get_latest_package_version('node', channel, os_type, cpu_arch_type)

    node_package_url = build_algo_release_url('node', channel, os_type, cpu_arch_type, node_package_version)
    if channel == 'test':
        node_package_url = build_algo_release_url('node', 'stable', os_type, cpu_arch_type, node_package_version)
    node_package_tar_path = f"{node_package_dir}/node_package.tar.gz"

    _ = urllib.request.urlretrieve(node_package_url, node_package_tar_path)
    file_util.decompressTarfile(node_package_tar_path, f"{node_package_dir}")

    file_util.mv_folder_contents(f"{node_package_dir}/data", data_dir)
    file_util.mv_folder_contents(f"{node_package_dir}/genesis", data_dir, ignore=True)
    file_util.mv_folder_contents(f"{node_package_dir}/bin", bin_dir)
    if not channel == 'stable':
        file_util.mv_file(
            os.path.join(data_dir, f"{channel}net/genesis.json"),
            os.path.join(data_dir, 'genesis.json')
        )

def configure_node(data_dir, kmd_dir, archival_node=False, algod_port=60000, kmd_port=60001):

    data_dir = file_util.ensure_folder(data_dir)
    kmd_dir = file_util.ensure_folder(kmd_dir)
    node_config_path = f"{data_dir}/config.json"
    kmd_config_path = f"{kmd_dir}/kmd_config.json"

    file_util.ensure_file(node_config_path, '{}')
    file_util.ensure_file(kmd_config_path, '{}')

    node_config = file_util.readJsonFile(node_config_path)
    kmd_config = file_util.readJsonFile(kmd_config_path)

    node_config['EndpointAddress'] = f"0.0.0.0:{algod_port}"
    node_config['Archival'] = archival_node
    if 'beta' in data_dir:
        node_config['DNSBootstrapID'] = '<network>.algodev.network'

    kmd_config['address'] = f"0.0.0.0:{kmd_port}"

    file_util.writeJsonFile(node_config_path, node_config)
    file_util.writeJsonFile(kmd_config_path, kmd_config)

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
