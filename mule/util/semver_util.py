from packaging import version
import re

def get_highest_version(semver_version_strings):
    semver_versions = list(
        map(
            lambda semver_version_string: version.parse(semver_version_string),
            semver_version_strings
        )
    )
    return str(max(semver_versions))

def parse_version(string):
    version_re = re.compile(r'(\d*)\.(\d*)\.(\d*)')
    return re.search(version_re, string).group(0)
