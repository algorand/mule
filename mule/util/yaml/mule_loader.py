import os
import re
import yaml
from mule.util import time_util
from mule.error import messages
from termcolor import cprint

env_var_path_matcher = re.compile(r'.*\$\{?([^}^{]+)\}?.*')

def env_var_path_constructor(loader, node):
    value = os.path.expandvars(node.value)
    if env_var_path_matcher.match(value):
        cprint(
            messages.CANNOT_EVALUATE_ENV_VAR.format(node.value),
            'yellow',
            attrs=['bold']
        )
        return ''
    return value

def timestamp_path_constructor(loader, node):
    return time_util.get_timestamp()

def getYamlLoaderWithEnvVars():
    yaml.add_implicit_resolver('!path', env_var_path_matcher)
    yaml.add_constructor('!path', env_var_path_constructor)
    yaml.add_constructor('!timestamp', timestamp_path_constructor)
    return yaml

def readYamlWithEnvVars(path):
    with open(path) as configs:
        loader = getYamlLoaderWithEnvVars()
        return loader.load(configs, Loader=yaml.FullLoader)
