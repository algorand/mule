import argparse
from mule import __version__


def parse_args():
    parser = argparse.ArgumentParser(
        description=f"Script for executing cicd (version {__version__})",
    )

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__,
    )

    parser.add_argument(
        '-a',
        '--archetype',
        help="Archetype project was built from (default: dropwizard)",
    )

    parser.add_argument(
        '-n',
        '--name',
        help="Name of application",
    )

    parser.set_defaults(which='all')

    subparsers = parser.add_subparsers(help='cicd actions')

    deps_action = subparsers.add_parser('deps', help='Install project deps')
    deps_action.set_defaults(which='deps')

    build_action = subparsers.add_parser('build', help='Build project binaries')
    build_action.set_defaults(which='build')

    publish_action = subparsers.add_parser('publish', help='Publish project binaries')
    publish_action.set_defaults(which='publish')
    publish_action.add_argument(
        '-e',
        '--environment',
        default='dev',
        help='environment of application artifacts are for'
    )

    deploy_action = subparsers.add_parser('deploy', help='Deploy project')
    deploy_action.set_defaults(which='deploy')
    deploy_action.add_argument(
        '-e',
        '--environment',
        default='dev',
        help='environment of application deployment is for'
    )

    undeploy_action = subparsers.add_parser('undeploy', help='Undeploy project')
    undeploy_action.set_defaults(which='undeploy')
    undeploy_action.add_argument(
        '-e',
        '--environment',
        required=True,
        help='environment of application to undeploy'
    )

    smoke_test_action = subparsers.add_parser('smoke_test', help='Smoke test project')
    smoke_test_action.set_defaults(which='smoke_test')
    smoke_test_action.add_argument(
        '-e',
        '--environment',
        required=True,
        help='environment of application to undeploy'
    )

    return parser.parse_args()
