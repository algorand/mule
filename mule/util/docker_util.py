import os
import subprocess
import hashlib

def run(image, command, work_dir):
    volume = f"{os.getcwd()}:{work_dir}"
    docker_command = f"docker run -ti --rm -v {volume} -w {work_dir} {image} {command}"
    subprocess.run(docker_command.split(" "), check=True)

# Build the docker image
def build(build_args, build_context_path, tags, docker_file_path):
    build_args_str = ""
    tags_str = ""
    if build_args is not None and len(build_args) > 0 :
        build_args_str = f"--build-arg {' --build-arg '.join(build_args)}"
    if tags is not None and len(tags) > 0 :
        tags_str = f"-t {' -t '.join(tags)}"
    docker_command = f"docker build {build_args_str} {tags_str} -f {docker_file_path} {build_context_path}"
    print(f"docker build command: '{docker_command}'")
    subprocess.run(docker_command.split(' '), check=True)

# Check docker hub for the image
def pullFromDockerHub(docker_image_name):
    found = False
    pull_from_docker_hub_command = f"docker pull {docker_image_name}"
    print(f"attempting to get image with command {pull_from_docker_hub_command}")
    docker_image_result = subprocess.run(pull_from_docker_hub_command.split(" "))
    if docker_image_result.returncode == 0:
        print(f"docker image found in docker hub '{docker_image_name}'")
        found = True
    else:
        print(f"docker file not found '{docker_image_name}' in docker hub")
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
        print(f"found local docker image '{docker_image_name}'")
        found = True
    else:
        print(f"local docker image not found '{docker_image_name}'")
    return found

# Ensure that the docker image exist for the current configuration file
def ensure(image, arch, build_context_path, docker_file_path):
    found = pullFromDockerHub(image)
    if not found :
        found = checkForLocalImage(image)
    if not found:
        print(f"building docker container for arch {arch}")
        build([f"ARCH={arch}"], build_context_path, [image], docker_file_path)

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
