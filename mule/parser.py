import argparse
from mule import __version__

def parseArgs():
    parser = argparse.ArgumentParser(
        description=f"Script for executing mule (version {__version__})"
    )

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__
    )

    parser.add_argument(
        '-f',
        '--file',
        default='mule.yaml',
        help="path to yaml defining mule stages (default: mule.yaml)"
    )

    parser.add_argument(
        'JOB',
        help="name of stage you would like to execute"
    )

    return parser.parse_args()
