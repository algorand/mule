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
    package_keys = list(s3_util.get_matching_s3_keys(
        'algorand-releases',
        f"channel/{channel}/{package_type}_{channel}_{os_type}-{cpu_arch_type}_",
        'tar.gz',
        s3_auth=False
    ))
    package_versions = list(map(semver_util.parse_version, package_keys))
    latest_version = semver_util.get_highest_version(package_versions)
    print(f"Found latest version of package type {package_type} for channel {channel}: {latest_version}")
    return latest_version

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

    print(f"Installing {channel} node package version {node_package_version} to:\n\tbin_dir: {bin_dir}\n\tdata_dir: {data_dir}")

    node_package_url = build_algo_release_url('node', channel, os_type, cpu_arch_type, node_package_version)
    if channel == 'test':
        node_package_url = build_algo_release_url('node', 'stable', os_type, cpu_arch_type, node_package_version)
    node_package_tar_path = f"{node_package_dir}/node_package.tar.gz"

    _ = urllib.request.urlretrieve(node_package_url, node_package_tar_path)
    file_util.decompressTarfile(node_package_tar_path, f"{node_package_dir}")

    file_util.mv_folder_contents(f"{node_package_dir}/data", data_dir)
    file_util.mv_folder_contents(f"{node_package_dir}/bin", bin_dir)
    if channel == 'stable':
        file_util.copy_file(
            os.path.join(node_package_dir, "genesis/mainnet/genesis.json"),
            os.path.join(data_dir, 'genesis.json')
        )
    else:
        file_util.copy_file(
            os.path.join(node_package_dir, f"genesis/{channel}net/genesis.json"),
            os.path.join(data_dir, 'genesis.json')
        )

def show_node_configs(data_dir, kmd_dir):
    data_dir = file_util.ensure_folder(data_dir)
    kmd_dir = file_util.ensure_folder(kmd_dir)
    node_config_path = f"{data_dir}/config.json"
    kmd_config_path = f"{kmd_dir}/kmd_config.json"

    file_util.ensure_file(node_config_path, '{}')
    file_util.ensure_file(kmd_config_path, '{}')

    current_node_config = file_util.read_json_file(node_config_path)
    current_kmd_config = file_util.read_json_file(kmd_config_path)

    print(f"Showing node configs at {node_config_path} with:\n{json.dumps(current_node_config, sort_keys=True, indent=4)}")
    print(f"Showing node configs at {kmd_config_path} with:\n{json.dumps(current_kmd_config, sort_keys=True, indent=4)}")

def configure_node(data_dir, kmd_dir, node_config, kmd_config):

    data_dir = file_util.ensure_folder(data_dir)
    kmd_dir = file_util.ensure_folder(kmd_dir)
    node_config_path = f"{data_dir}/config.json"
    kmd_config_path = f"{kmd_dir}/kmd_config.json"

    file_util.ensure_file(node_config_path, '{}')
    file_util.ensure_file(kmd_config_path, '{}')

    current_node_config = file_util.read_json_file(node_config_path)
    current_kmd_config = file_util.read_json_file(kmd_config_path)

    current_node_config.update(node_config)
    current_kmd_config.update(kmd_config)

    print(f"Updating node configs at {node_config_path} with:\n{json.dumps(node_config, sort_keys=True, indent=4)}")
    print(f"Updating node configs at {kmd_config_path} with:\n{json.dumps(kmd_config, sort_keys=True, indent=4)}")

    file_util.write_json_file(node_config_path, current_node_config)
    file_util.write_json_file(kmd_config_path, current_kmd_config)

def start_node(data_dir, kmd_dir, bin_dir=None):
    goal_args = [
        'node',
        'start',
    ]
    print(f"Starting node with:\n\tdata_dir: {data_dir}\n\tkmd_dir: {kmd_dir}")
    goal(data_dir, kmd_dir, goal_args, bin_dir)

def stop_node(data_dir, kmd_dir, bin_dir=None):
    goal_args = [
        'node',
        'stop',
    ]
    print(f"Stopping node with:\n\tdata_dir: {data_dir}\n\tkmd_dir: {kmd_dir}")
    goal(data_dir, kmd_dir, goal_args, bin_dir)

def restart_node(data_dir, kmd_dir, bin_dir=None):
    goal_args = [
        'node',
        'restart',
    ]
    print(f"Restarting node with:\n\tdata_dir: {data_dir}\n\tkmd_dir: {kmd_dir}")
    goal(data_dir, kmd_dir, goal_args, bin_dir)

def status_node(data_dir, kmd_dir, bin_dir=None):
    goal_args = [
        'node',
        'status',
    ]
    print(f"Status of node with:\n\tdata_dir: {data_dir}\n\tkmd_dir: {kmd_dir}")
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

def algorand_indexer(args, bin_dir=None, log_file_name=None):
    algorand_indexer_command = ['algorand-indexer']
    if not bin_dir is None:
        algorand_indexer_command = [f"{bin_dir}/algorand-indexer"]
    if log_file_name is None:
        log_file_name = f"indexer-{time_util.get_timestamp()}.log"

    algorand_indexer_command.extend(args)
    log_file = open(log_file_name, 'w')
    subprocess.Popen(algorand_indexer_command, stdout=log_file, stderr=log_file)

def start_indexer_local_node(node, postgres, bin_dir=None, pid_file=None, log_file_name=None):
    algorand_indexer_args = ['daemon']

    algorand_indexer_args.extend([
        '-d', node['data'],
        '--postgres', build_indexer_postgress_connection_string(postgres)
    ])

    if not pid_file is None:
        algorand_indexer_args.extend([
            '--pidfile', pid_file
        ])

    algorand_indexer(algorand_indexer_args, bin_dir, log_file_name)

def start_indexer_remote_node(node, postgres, bin_dir=None, pid_file=None, log_file_name=None):
    algorand_indexer_args = ['daemon']

    algorand_indexer_args.extend([
        '--algod-net', f"{node['host']}:{node['port']}",
        '--algod-token', node['token'],
        '--genesis', node['genesis'],
        '--postgres', build_indexer_postgress_connection_string(postgres)
    ])

    if not pid_file is None:
        algorand_indexer_args.extend([
            '--pidfile', pid_file
        ])

    algorand_indexer(algorand_indexer_args, bin_dir, log_file_name)

def build_indexer_postgress_connection_string(postgres):
    postgress_connection_string = []
    for field in postgres.items():
        postgress_connection_string.append(f"{field[0]}={field[1]}")
    return ' '.join(postgress_connection_string)
