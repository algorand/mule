import json

from mule.util import shell_util


def build():
    run_package_script('build')


def test():
    run_package_script('test')


def run_package_script(script):
    shell_util.run(['npm', 'run', script])


def get_version():
    return get_field_from_package('version')


def get_name():
    return get_field_from_package('name')


def get_field_from_package(field: str):
    with open('package.json') as f:
        package_json = json.load(f)
        return package_json[field]

