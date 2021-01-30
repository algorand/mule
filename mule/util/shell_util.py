import subprocess


shell_runner = subprocess.run


def run(command, capture_output=False, check=True):
    shell_runner(command, check=check, capture_output=capture_output)
