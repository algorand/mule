import atexit
import hashlib
import os
import re
import subprocess
from termcolor import cprint
import time

from mule.task import ITask
from mule.error import messages
from mule.util import update_dict

import ipdb

class IDockerTask(ITask):
#    required_typed_fields = [
#        ('docker', dict),
#        ('docker.image', str),
#        ('docker.version', str),
#    ]
#    optional_typed_fields = [
#        ('docker.workDir', str),
#        ('docker.env', list),
#        ('docker.shell', str),
#    ]

    def __init__(self, args):
        super().__init__(args)
#        self.docker = update_dict(
#            {
#                'workDir': '/project',
#                'env': [],
#                'volumes': [],
#            },
#            args['docker'],
#        )
#        self.validateDockerConfigs()

    def execute(self, job_context):
        super().execute(job_context)
        self.run(
            f"{self.docker['image']}:{self.docker['version']}",
#            [self.docker['shell'], '-c', self.command],
            ['bash', '-c', self.command],
            self.docker['workDir'],
            self.docker['volumes'],
            self.docker['env'],
        )

    # This takes container name
    def kill(self, container_name):
        if(len(subprocess.run(f"docker ps -q -f name=^/{container_name}$".split(' '), capture_output=True).stdout) > 0):
            print(f"Cleaning up started docker container {container_name}")
            subprocess.run(f"docker kill {container_name}".split(' '), stdout=subprocess.DEVNULL)

    def run(self, image, command, work_dir, volumes, env):
        container_name = f"mule-{time.time_ns()}"
        docker_command = ['docker', 'run', '--name', container_name, '--rm', '-w', work_dir, '-i', '-v', f"{os.getcwd()}:{work_dir}"]

        for env_var in env:
            docker_command.extend(['--env', env_var])
        for volume in volumes:
            docker_command.extend(['-v', volume])

        docker_command.append(image)
        docker_command.extend(command)
        atexit.register(self.kill, container_name)
        subprocess.run(docker_command, check=True)

    def validateDockerConfigs(self):
        # Validate docker env var onfigs are all strings
        for env_var_index, env_var in enumerate(self.docker['env']):
            if not type(env_var) == str:
                raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                    self.getId(),
                    f"docker.env[{env_var_index}]",
                    str,
                    type(env_var)
                ))
        dockerEnvVarPattern = re.compile(r'.*=.+')
        self.docker['env'] = [envVar for envVar in self.docker['env'] if dockerEnvVarPattern.match(envVar)]

        for volume_index, volume in enumerate(self.docker['volumes']):
            if not type(volume) == str:
                raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                    self.getId(),
                    f"docker.env[{volume_index}]",
                    str,
                    type(volume)
                ))
        dockerVolumePattern = re.compile(r'.+:.+')
        self.docker['volumes'] = [volume for volume in self.docker['volumes'] if dockerVolumePattern.match(volume)]

        if not 'shell' in self.docker.keys():
            self.docker['shell'] = 'bash'

class Machine(IDockerTask):
    required_fields = [
        'image',
    ]

    docker = {
        'arch': 'amd64',
        'dockerFilePath': 'Dockerfile',
        'env': [],
        'image': '',
        'version': 'latest',
        'volumes': [],
        'workDir': '.',
    }

    def __init__(self, args):
        ipdb.set_trace()
        super().__init__(args)
        if 'image' in args:
            self.docker['image'] = args['image']
        if 'arch' in args:
            self.docker['arch'] = args['arch']
        if 'dockerFilePath' in args:
            self.docker['dockerFilePath'] = args['dockerFilePath']
        if 'env' in args:
            self.docker['env'] = args['env']
        if 'volumes' in args:
            self.docker['volumes'] = args['volumes']
        if 'workDir' in args:
            self.docker['workDir'] = args['workDir']

    def execute(self, job_context):
        self.docker['version'] = f"{self.docker['arch']}-{self.compute_digest()}"
        self.ensure()
        super().execute(job_context)

    def build(self, image):
        build_args = [f"ARCH={self.docker['arch']}"]
        build_args_str = ""
        tags = [image]
        tags_str = ""
        if build_args is not None and len(build_args) > 0 :
            build_args_str = f"--build-arg {' --build-arg '.join(build_args)}"
        if tags is not None and len(tags) > 0 :
            tags_str = f"-t {' -t '.join(tags)}"
        docker_command = f"docker build {build_args_str} {tags_str} -f {self.docker['dockerFilePath']} {self.docker['workDir']}"
        subprocess.run(docker_command.split(' '), check=True)

    def checkForLocalImage(self, image):
        found = False
        check_for_local_docker_image = f"docker inspect --type=image {image}"
        docker_inspect_result = subprocess.run(
            check_for_local_docker_image.split(" "),
            stdout=subprocess.DEVNULL
        )
        if docker_inspect_result.returncode == 0:
            found = True
        return found

    def compute_digest(self):
        BLOCK_SIZE = 65536
        file_hash = hashlib.sha1()
        with open(self.docker['dockerFilePath'], 'rb') as f:
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(BLOCK_SIZE)
        return file_hash.hexdigest()

    def ensure(self):
        image = f"{self.docker['image']}:{self.docker['version']}"
        if self.checkForLocalImage(image):
            cprint(
                f"Found docker image {image} locally",
                'green',
            )
        else:
            if self.pullFromDockerHub(image):
                cprint(
                    f"Found docker image {image} on DockerHub",
                    'green',
                )
            else:
                self.build(image)
                cprint(
                    f"Built docker image {image} from {self.docker['dockerFilePath']}",
                    'green',
                )

    def pullFromDockerHub(self, image):
        found = False
        pull_from_docker_hub_command = f"docker pull {self.docker['image']}"
        docker_image_result = subprocess.run(pull_from_docker_hub_command.split(" "))
        if docker_image_result.returncode == 0:
            found = True
        return found

class Make(IDockerTask):
    required_fields = [
        'target'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.target = args['target']
        self.command = f"make {self.target}"

    def execute(self, job_context):
        super().execute(job_context)

class Shell(IDockerTask):
    required_fields = [
        'command',
    ]

    def __init__(self, args):
        super().__init__(args)
        self.command = args['command']

    def execute(self, job_context):
        super().execute(job_context)

