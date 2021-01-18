import atexit
import hashlib
import os
import re
import subprocess
import time

from mule.error import messages
from mule.logger import logger
from mule.task import ITask


# TODO: isolate all `subprocess.run` calls to a single location

class Docker(ITask):
    required_fields = [
        'image',
    ]

    machine = {
        'arch': 'amd64',
        'buildArgs': [],
        'context': '.',
        'destroy': True,
        'dockerFilePath': 'Dockerfile',
        'env': [],
        'image': '',
        'shell': 'bash',
        'tag': 'latest',
        'version': '',
        'volumes': [],
        'workDir': '/project',
    }

    def __init__(self, args):
        super().__init__(args)

    def build(self, full_image_name):
        build_args = [f"ARCH={self.machine['arch']}"] + self.eval_args(self.machine['buildArgs'])
        build_args_str = f"--build-arg {' --build-arg '.join(build_args)}"
        docker_command = f"docker build {build_args_str} {full_image_name} -f {self.machine['dockerFilePath']} {self.machine['context']}"
        subprocess.run(docker_command.split(' '), check=True)

    # The mule schema supports defining agent.{env,volumes} as either dicts or lists,
    # but we want to operate on lists in this module because it's easier to build out
    # the docker api.
    #
    # Also, remove any items that have an empty string as a value.
    def check_block_format(self, obj, delimiter):
        if type(obj) is dict:
            return [f"{k}{delimiter}{v}" for k, v in obj.items() if v]
        return list(filter(None, obj))

    def check_for_local_image(self, full_image_name):
        found = False
        check_for_local_docker_image = f"docker inspect --type=image {full_image_name}"
        docker_inspect_result = subprocess.run(
            check_for_local_docker_image.split(" "),
            stdout=subprocess.DEVNULL
        )
        if docker_inspect_result.returncode == 0:
            found = True
        return found

    def ensure(self, full_image_name):
        if self.check_for_local_image(full_image_name):
            logger.info(f"Found docker image {full_image_name} locally")
        else:
            if self.pull_from_docker_hub(full_image_name):
                logger.info(f"Found docker image {full_image_name} on DockerHub")
            else:
                self.build(full_image_name)
                logger.info(f"Built docker image {full_image_name} from {self.machine['dockerFilePath']}")

    def execute(self, full_image_name):
        self.ensure(full_image_name)
        self.run(full_image_name)

    def eval_args(self, args_list):
        args = []
        for arg in args_list:
            # If an env var isn't set, then `arg` will be empty ("").
            # This *usually* is ok, as env vars can be optional.
            if arg:
                symbol, value = arg.split('=')
                if value[0] == '`':
                    ret = subprocess.run(value.strip('`').split(), capture_output=True)
                    args.append('='.join((symbol, ret.stdout.decode('utf-8').rstrip('\n'))))
                else:
                    args.append(arg)
        return args

    def get_full_image_name(self, image):
        return ":".join((image, self.machine['tag']))

    def kill(self, container_name):
        if(len(subprocess.run(f"docker ps -q -f name=^/{container_name}$".split(' '), capture_output=True).stdout) > 0):
            logger.info(f"Cleaning up started docker container {container_name}")
            subprocess.run(f"docker kill {container_name}".split(' '), stdout=subprocess.DEVNULL)

    def pull_from_docker_hub(self, full_image_name):
        found = False
        pull_from_docker_hub_command = f"docker pull {full_image_name}"
        docker_image_result = subprocess.run(pull_from_docker_hub_command.split(" "))
        if docker_image_result.returncode == 0:
            found = True
        return found

    def run(self, full_image_name):
        work_dir = self.machine['workDir']
        rm_container = '--rm' if self.machine['destroy'] else ''
        container_name = f"mule-{time.time_ns()}"
        docker_command = ['docker', 'run', '--name', container_name, rm_container, '-w', work_dir, '-i', '-v', f"{os.getcwd()}:{work_dir}"]

        for env_var in self.check_block_format(self.machine['env'], "="):
            docker_command.extend(['--env', env_var])

        for volume in self.check_block_format(self.machine['volumes'], ":"):
            docker_command.extend(['-v', volume])

        docker_command.append(full_image_name)
        docker_command.extend([self.machine['shell'], '-c', self.command])
        atexit.register(self.kill, container_name)
        subprocess.run(docker_command, check=True)


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
        super().execute(f"{self.machine['image']}:{self.machine['tag']}")


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
