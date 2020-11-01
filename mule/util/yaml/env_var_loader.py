from termcolor import cprint
import os
import re
import yaml

from mule.error import messages

env_var_path_matcher = re.compile(r'.*\$\{?([^}^{]+)\}?.*')
tag = '!path'

def path_constructor(loader, node):
    value = os.path.expandvars(node.value)
    if env_var_path_matcher.match(value):
        cprint(
            messages.CANNOT_EVALUATE_ENV_VAR.format(node.value),
            'yellow',
            attrs=['bold']
        )
        return ''
    return value

def resolveEnvVars():
    yaml.add_implicit_resolver(tag, env_var_path_matcher)
    yaml.add_constructor(tag, path_constructor)
    return yaml

def readYaml(mule_config, raw=True):
    loader = yaml
    stream = yaml.dump(mule_config)

    if not raw:
        loader = resolveEnvVars()

    return loader.load(stream, Loader=yaml.FullLoader)

