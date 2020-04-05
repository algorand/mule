import argparse
from mule import __version__

def parseArgs():
    parser = argparse.ArgumentParser(
        description=f"Script for executing mule (version {__version__})",
    )

    parser.add_argument(
        '-v',
        '--version',
        action = 'version',
        version = __version__,
    )

    parser.add_argument(
        '-f',
        '--file',
        default = 'mule.yaml',
        help = "path to yaml defining mule jobs (default: mule.yaml)",
    )
    group = parser.add_mutually_exclusive_group(
        required=True,
    )

    group.add_argument(
        '--list-jobs',
        action = 'store_true',
        dest = 'list_jobs',
        help = 'lists jobs in mule yaml file',
    )

    group.add_argument(
        '--list-tasks',
        action = 'store_true',
        dest = 'list_tasks',
        help = 'lists tasks in mule yaml file',
    )

    group.add_argument(
        'JOB',
        help="name of job you would like to execute",
        nargs='?',
        default = None,
    )

    return parser.parse_args()
