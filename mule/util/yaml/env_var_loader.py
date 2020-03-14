import os
import re
import yaml
from mule.error import messages

env_var_path_matcher = re.compile(r'.*\$\{([^}^{]+)\}.*')

def path_constructor(loader, node):
    value = os.path.expandvars(node.value)
    if env_var_path_matcher.match(value):
        print(messages.CANNOT_EVALUATE_ENV_VAR.format(node.value))
        exit(1)
    return os.path.expandvars(node.value)

def getYamlLoaderWithEnvVars():
    yaml.add_implicit_resolver('!path', env_var_path_matcher)
    yaml.add_constructor('!path', path_constructor)
    return yaml

def readYamlWithEnvVars(stream):
    loader = getYamlLoaderWithEnvVars()
    return loader.load(stream, Loader=yaml.FullLoader)
