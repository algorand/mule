import mule.ci.archetype.util
from mule.ci import parser, config
from mule.util import file_util


def main():
    args = parser.parse_args()
    config = build_config(args)
    validate_config(config)
    archetypes = mule.ci.archetype.util.get_archetypes()
    if config['archetype'] in archetypes:
        archetype_instance = mule.ci.archetype.util.get_archetype(config['archetype'], config['application_name'])
        if args.which == 'deps':
            archetype_instance.deps()
        if args.which == 'build':
            archetype_instance.build()
        elif args.which == 'publish':
            archetype_instance.publish(args.environment)
        elif args.which == 'deploy':
            archetype_instance.deploy(args.environment)
        elif args.which == 'undeploy':
            archetype_instance.undeploy(args.environment)
        elif args.which == 'smoke_test':
            archetype_instance.smoke_test(args.environment)


def build_config(args):
    config = read_config()
    if args.archetype is not None:
        config['archetype'] = args.archetype
    if args.name is not None:
        config['application_name'] = args.name
    return config


def validate_config(config):
    if 'application_name' not in config:
        raise Exception('Application name must be provided through cli arguement or .cicd_config.yml file')


def read_config():
    if file_util.is_file(config.MULE_FILE_PATH):
        return file_util.read_yaml_file(config.MULE_FILE_PATH)
    return {}
