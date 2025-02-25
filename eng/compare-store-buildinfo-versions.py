#!/usr/bin/env python3

import argparse
from enum import Enum
import re
import requests
import subprocess
import sys

class VersionComparison(Enum):
    EQUAL = 0
    STORE_OLDER = 1
    STORE_NEWER = 2
    UNABLE_TO_COMPARE = 3

def usage():
    print("Usage: script.py --snap-name <snap-name> --buildinfo-url <buildinfo-url>")
    sys.exit(1)

def compare_versions(store_version: str, buildinfo_version: str) -> VersionComparison:
    """
    Compare two PowerShell versions and return the result.

    :param store_version: The current PowerShell version in the Snap Store
    :param buildinfo_version: The current PowerShell version in the buildinfo file
    :return: `VersionComparison.EQUAL` if the versions are the same,
             `VersionComparison.STORE_OLDER` if the store version is older,
             `VersionComparison.STORE_NEWER` if the store version is newer
    """
    version_pattern = r'^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?(\.[0-9]+)?$'
    
    if not re.match(version_pattern, store_version):
        print(f"Invalid version format: {store_version}")
        return VersionComparison.UNABLE_TO_COMPARE
    if not re.match(version_pattern, buildinfo_version):
        print(f"Invalid version format: {buildinfo_version}")
        return VersionComparison.UNABLE_TO_COMPARE

    store_version_split = re.split(r'[.-]', store_version)
    buildinfo_version_split = re.split(r'[.-]', buildinfo_version)

    for i in range(3):
        if int(store_version_split[i]) < int(buildinfo_version_split[i]):
            return VersionComparison.STORE_OLDER
        elif int(store_version_split[i]) > int(buildinfo_version_split[i]):
            return VersionComparison.STORE_NEWER

    # store has a pre-release version, while buildinfo does not
    if len(store_version_split) > 3 and len(buildinfo_version_split) <= 3:
        return VersionComparison.STORE_OLDER
    # store does not have a pre-release version, while buildinfo does
    elif len(store_version_split) <= 3 and len(buildinfo_version_split) > 3:
        return VersionComparison.STORE_NEWER

    # both the store and buildinfo have pre-release versions
    if len(store_version_split) > 3 and len(buildinfo_version_split) > 3:
        if store_version_split[3] < buildinfo_version_split[3]:
            return VersionComparison.STORE_OLDER
        elif store_version_split[3] > buildinfo_version_split[3]:
            return VersionComparison.STORE_NEWER
        else:
            # both pre-release types are the same (alpha, preview, rc, etc.)
            # now compare the pre-release version
            if store_version_split[4] < buildinfo_version_split[4]:
                return VersionComparison.STORE_OLDER
            elif store_version_split[4] > buildinfo_version_split[4]:
                return VersionComparison.STORE_NEWER

    return VersionComparison.EQUAL

def print_result(result: str, output_file: str | None):
    print(result)
    if (output_file):
        with open(output_file, 'w') as f:
            f.write(result)
            f.write('\n')

def main():
    parser = argparse.ArgumentParser(description='Compare versions.')
    parser.add_argument('--snap-name', required=True, help='Snap name')
    parser.add_argument('--snap-channel', required=True, help='Snap channel')
    parser.add_argument('--buildinfo-url', required=True, help='Buildinfo URL')
    parser.add_argument('--output-file', required=False, help='File to print script output to')
    args = parser.parse_args()

    snap_name = args.snap_name
    snap_channel = args.snap_channel
    buildinfo_url = args.buildinfo_url
    output_file = args.output_file

    try:
        latest_store_version = subprocess.check_output(
            ["snap", "info", snap_name], universal_newlines=True
        ).splitlines()
        latest_store_version = next(
            (line.split()[1] for line in latest_store_version if f"{snap_channel}:" in line), None
        )
    except subprocess.CalledProcessError:
        print("Failed to get the latest version of the snap")
        sys.exit(1)

    try:
        response = requests.get(buildinfo_url)
        response.raise_for_status()
        latest_buildinfo_version = response.json().get('ReleaseTag', '').lstrip('v')
    except requests.RequestException:
        print("Failed to get the latest version from the buildinfo")
        sys.exit(1)

    if not latest_store_version or not latest_buildinfo_version:
        print("Failed to get the latest version of the snap or the latest version from the buildinfo")
        sys.exit(1)

    result = compare_versions(latest_store_version, latest_buildinfo_version)

    if result == VersionComparison.STORE_OLDER:
        result = f"The latest version in the store ({latest_store_version}) is older than the latest version in the buildinfo ({latest_buildinfo_version})"
        print_result(result, output_file)
        sys.exit(0)
    elif result == VersionComparison.STORE_NEWER:
        result = f"The latest version in the store ({latest_store_version}) is newer than the latest version in the buildinfo ({latest_buildinfo_version})"
        print_result(result, output_file)
        sys.exit(1)
    elif result == VersionComparison.EQUAL:
        result = f"The latest version in the store ({latest_store_version}) is the same as the latest version in the buildinfo ({latest_buildinfo_version})"
        print_result(result, output_file)
        sys.exit(1)
    else:
        result = "Unable to compare the versions"
        print_result(result, output_file)
        sys.exit(1)

if __name__ == "__main__":
    main()
