import subprocess

# Build the docker image
from mule.util import shell_util


def build(tags, build_args=[], docker_file_path='Dockerfile', build_context_path='.'):
    docker_command = ['docker', 'build']
    if build_args is not None and len(build_args) > 0 :
        for build_arg in build_args:
            docker_command.extend(['--build-arg', build_arg])
    if tags is not None and len(tags) > 0:
        for tag in tags:
            docker_command.extend(['-t', tag])
    docker_command.extend(['-f', docker_file_path, build_context_path])
    shell_util.run(docker_command, check=True)


# Push docker images
def push(images):
    for image in images:
        if image is not None and len(image) > 0:
            shell_util.run(['docker', 'push', image], check=True)


# Push docker images
def tag(source, target):
    shell_util.run(['docker', 'tag', source, target], check=True)
