import os
import subprocess
import hashlib
import sys
import time
import atexit
from termcolor import cprint

def run(image, command, work_dir, volumes, env):
    container_name = f"mule-{time.time_ns()}"
    docker_command = ['docker', 'run', '--name', container_name, '--rm', '-w', work_dir, '-i', '-v', f"{os.getcwd()}:{work_dir}"]

    for env_var in env:
        docker_command.extend(['--env', env_var])
    for volume in volumes:
        docker_command.extend(['-v', volume])

    docker_command.append(image)
    docker_command.extend(command)
    atexit.register(kill, container_name)
    subprocess.run(docker_command, check=True)

# This takes container name
def kill(container_name):
    if(len(subprocess.run(f"docker ps -q -f name=^/{container_name}$".split(' '), capture_output=True).stdout) > 0):
        print(f"Cleaning up started docker container {container_name}")
        subprocess.run(f"docker kill {container_name}".split(' '), stdout=subprocess.DEVNULL)

# Build the docker image
def build(build_args, build_context_path, tags, docker_file_path):
    build_args_str = ""
    tags_str = ""
    if build_args is not None and len(build_args) > 0 :
        build_args_str = f"--build-arg {' --build-arg '.join(build_args)}"
    if tags is not None and len(tags) > 0 :
        tags_str = f"-t {' -t '.join(tags)}"
    docker_command = f"docker build {build_args_str} {tags_str} -f {docker_file_path} {build_context_path}"
    subprocess.run(docker_command.split(' '), check=True)

# Check docker hub for the image
def pullFromDockerHub(docker_image_name):
    found = False
    pull_from_docker_hub_command = f"docker pull {docker_image_name}"
    docker_image_result = subprocess.run(pull_from_docker_hub_command.split(" "))
    if docker_image_result.returncode == 0:
        found = True
    return found

# Check for local image
def checkForLocalImage(docker_image_name) :
    found = False
    check_for_local_docker_image = f"docker inspect --type=image {docker_image_name}"
    docker_inspect_result = subprocess.run(
        check_for_local_docker_image.split(" "),
        stdout=subprocess.DEVNULL
    )
    if docker_inspect_result.returncode == 0:
        found = True
    return found

# Ensure that the docker image exist for the current configuration file
def ensure(image, arch, build_context_path, docker_file_path):
    if checkForLocalImage(image):
        cprint(
            f"Found docker image {image} locally",
            'green',
        )
    else:
        if pullFromDockerHub(image):
            cprint(
                f"Found docker image {image} on DockerHub",
                'green',
            )
        else:
            build([f"ARCH={arch}"], build_context_path, [image], docker_file_path)
            cprint(
                f"Built docker image {image} from {docker_file_path}",
                'green',
            )

# Construct the version
def getVersion(arch, config_file):
    checksum = compute_digest(config_file)
    return f"{arch}-{checksum}"

# Compute the SHA1 digest for a file
def compute_digest(file):
    BLOCK_SIZE = 65536
    file_hash = hashlib.sha1()
    with open(file, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)
    return file_hash.hexdigest()
