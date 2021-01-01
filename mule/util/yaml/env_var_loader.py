from termcolor import cprint
import os
import re
import yaml

from mule.error import messages
from mule.logger import logger

env_var_path_matcher = re.compile(r'.*\$\{?([^}^{]+)\}?.*')
tag = '!path'

def path_constructor(loader, node):
    value = os.path.expandvars(node.value)
    if env_var_path_matcher.match(value):
        logger.info("you are a foo")
#        cprint(
#            messages.CANNOT_EVALUATE_ENV_VAR.format(node.value),
#            'yellow',
#            attrs=['bold']
#        )
        return ''
    return value

def get_loader(raw):
    if not raw:
        # Evaluate the env vars.
        yaml.add_implicit_resolver(tag, env_var_path_matcher)
        yaml.add_constructor(tag, path_constructor)
        return yaml
    return yaml

def read_yaml(mule_config, raw=True):
    stream = yaml.dump(mule_config)
    return get_loader(raw).load(stream, Loader=yaml.FullLoader)

