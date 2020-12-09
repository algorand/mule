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

# TODO: isolate all `subprocess.run` calls to a single location

class Docker(ITask):
    required_fields = [
        'image',
    ]

    machine = {
        'arch': 'amd64',
        'buildArgs': [],
        'destroy': True,
        'dockerFilePath': 'Dockerfile',
        'env': [],
        'image': '',
        'shell': 'bash',
        'version': '',
        'volumes': [],
        'workDir': '/project',
        'context': '.'
    }

    def __init__(self, args):
        super().__init__(args)

    def build(self, image):
        build_args = [f"ARCH={self.machine['arch']}"] + self.eval_args(self.machine['buildArgs'])
        build_args_str = ""
        tags = [image]
        tags_str = ""
        if build_args is not None and len(build_args) > 0 :
            build_args_str = f"--build-arg {' --build-arg '.join(build_args)}"
        if tags is not None and len(tags) > 0 :
            tags_str = f"-t {' -t '.join(tags)}"
        docker_command = f"docker build {build_args_str} {tags_str} -f {self.machine['dockerFilePath']} {self.machine['context']}"
        subprocess.run(docker_command.split(' '), check=True)

    def check_for_local_image(self, image):
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
        if self.check_for_local_image(image):
            cprint(
                f"Found docker image {image} locally",
                'green',
            )
        else:
            if self.pull_from_docker_hub(image):
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
        self.run(image)

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

    def kill(self, container_name):
        if(len(subprocess.run(f"docker ps -q -f name=^/{container_name}$".split(' '), capture_output=True).stdout) > 0):
            print(f"Cleaning up started docker container {container_name}")
            subprocess.run(f"docker kill {container_name}".split(' '), stdout=subprocess.DEVNULL)

    def pull_from_docker_hub(self, image):
        found = False
        pull_from_docker_hub_command = f"docker pull {image}"
        docker_image_result = subprocess.run(pull_from_docker_hub_command.split(" "))
        if docker_image_result.returncode == 0:
            found = True
        return found

    def run(self, image):
        work_dir = self.machine['workDir']
        rm_container = '--rm' if self.machine['destroy'] else ''
        container_name = f"mule-{time.time_ns()}"
        docker_command = ['docker', 'run', '--name', container_name, rm_container, '-w', work_dir, '-i', '-v', f"{os.getcwd()}:{work_dir}"]

        for env_var in self.eval_args(self.machine['env']):
            docker_command.extend(['--env', env_var])
        for volume in self.validate_volumes(self.machine['volumes']):
            docker_command.extend(['-v', volume])

        docker_command.append(image)
        docker_command.extend([self.machine['shell'], '-c', self.command])
        atexit.register(self.kill, container_name)
        subprocess.run(docker_command, check=True)

    def validate_volumes(self, volumes):
        volume_re = re.compile(r'.+:.+')
        bad_volumes = [volume for volume in volumes if not volume_re.match(volume)]
        if len(bad_volumes):
            raise Exception(messages.BAD_VOLUME_CONFIG.format(", ".join(bad_volumes)))
        return volumes


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


