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

class Docker(ITask):
    required_fields = [
        'image',
    ]

    machine = {
        'arch': 'amd64',
        'buildArgs': [],
        'dockerFilePath': 'Dockerfile',
        'env': [],
        'image': '',
        'shell': 'bash',
        'version': '',
        'volumes': [],
        'workDir': '/project',
    }

    def __init__(self, args):
        super().__init__(args)

    def build(self, image):
        build_args = [f"ARCH={self.machine['arch']}"] + self.evaluateBuildArgs()
        build_args_str = ""
        tags = [image]
        tags_str = ""
        if build_args is not None and len(build_args) > 0 :
            build_args_str = f"--build-arg {' --build-arg '.join(build_args)}"
        if tags is not None and len(tags) > 0 :
            tags_str = f"-t {' -t '.join(tags)}"
        docker_command = f"docker build {build_args_str} {tags_str} -f {self.machine['dockerFilePath']} {self.machine['workDir']}"
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
        with open(self.machine['version'], 'rb') as f:
            fb = f.read(BLOCK_SIZE)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(BLOCK_SIZE)
        return file_hash.hexdigest()

    def ensure(self, image):
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
                    f"Built docker image {image} from {self.machine['dockerFilePath']}",
                    'green',
                )

    def execute(self, image):
        self.ensure(image)
        self.validateDockerConfigs()
        self.run(
            image,
            [self.machine['shell'], '-c', self.command],
            self.machine['workDir'],
            self.machine['volumes'],
            self.machine['env'],
        )

    def evaluateBuildArgs(self):
        args = []
        for build_arg in self.machine['buildArgs']:
            symbol, value = build_arg.split('=')
            if value[0] == '`':
                ret = subprocess.run(value.strip('`'), capture_output=True)
                args.append('='.join((symbol, ret.stdout.decode('utf-8').rstrip('\n'))))
            else:
                args.append(build_arg)
        return args

    def kill(self, container_name):
        if(len(subprocess.run(f"docker ps -q -f name=^/{container_name}$".split(' '), capture_output=True).stdout) > 0):
            print(f"Cleaning up started docker container {container_name}")
            subprocess.run(f"docker kill {container_name}".split(' '), stdout=subprocess.DEVNULL)

    def pullFromDockerHub(self, image):
        found = False
        pull_from_docker_hub_command = f"docker pull {self.machine['image']}"
        docker_image_result = subprocess.run(pull_from_docker_hub_command.split(" "))
        if docker_image_result.returncode == 0:
            found = True
        return found

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
        for env_var_index, env_var in enumerate(self.machine['env']):
            if not type(env_var) == str:
                raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                    self.getId(),
                    f"docker.env[{env_var_index}]",
                    str,
                    type(env_var)
                ))
        dockerEnvVarPattern = re.compile(r'.*=.+')
        self.machine['env'] = [envVar for envVar in self.machine['env'] if dockerEnvVarPattern.match(envVar)]

        for volume_index, volume in enumerate(self.machine['volumes']):
            if not type(volume) == str:
                raise Exception(messages.TASK_FIELD_IS_WRONG_TYPE.format(
                    self.getId(),
                    f"docker.env[{volume_index}]",
                    str,
                    type(volume)
                ))
        dockerVolumePattern = re.compile(r'.+:.+')
        self.machine['volumes'] = [volume for volume in self.machine['volumes'] if dockerVolumePattern.match(volume)]


class Make(Docker):
    required_fields = [
        'agent',
        'target'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.agent = args['agent']
        self.target = args['target']
        self.command = f"make {self.target}"

    def execute(self, job_context):
        machine_config = [agent for agent in job_context.get_field('agents') if agent['name'] == self.agent]
        if len(machine_config) == 0:
            raise Exception(messages.MACHINE_MISSING_NAME.format(self.agent))
        elif len(machine_config) > 1:
            raise Exception(messages.MACHINE_DUPLICATE_NAME.format(self.agent))
        self.machine.update(machine_config[0])
        super().execute(f"{self.machine['image']}:{self.machine['arch']}-{self.compute_digest()}")


class Shell(Docker):
    required_fields = [
        'agent',
        'command'
    ]

    def __init__(self, args):
        super().__init__(args)
        self.agent = args['agent']
        self.command = args['command']

    def execute(self, job_context):
        super().execute(self.agent)


