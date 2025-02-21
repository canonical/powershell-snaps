#!/usr/bin/env python3

import argparse
import re
import subprocess
import requests
import sys

def usage():
    print("Usage: script.py --snap-name <snap-name> --buildinfo-url <buildinfo-url>")
    sys.exit(1)

def compare_versions(version1, version2):
    version_pattern = r'^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?(\.[0-9]+)?$'
    
    if not re.match(version_pattern, version1):
        print(f"Invalid version format: {version1}")
        return 1
    if not re.match(version_pattern, version2):
        print(f"Invalid version format: {version2}")
        return 1

    v1 = re.split(r'[.-]', version1)
    v2 = re.split(r'[.-]', version2)

    for i in range(3):
        if int(v1[i]) < int(v2[i]):
            return 1
        elif int(v1[i]) > int(v2[i]):
            return 2

    if len(v1) > 3 and len(v2) <= 3:
        return 1
    elif len(v1) <= 3 and len(v2) > 3:
        return 2

    if len(v1) > 3 and len(v2) > 3:
        if v1[3] < v2[3]:
            return 1
        elif v1[3] > v2[3]:
            return 2

    return 0

def main():
    parser = argparse.ArgumentParser(description='Compare versions.')
    parser.add_argument('--snap-name', required=True, help='Snap name')
    parser.add_argument('--snap-channel', required=True, help='Snap channel')
    parser.add_argument('--buildinfo-url', required=True, help='Buildinfo URL')
    args = parser.parse_args()

    snap_name = args.snap_name
    snap_channel = args.snap_channel
    buildinfo_url = args.buildinfo_url

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

    if result == 1:
        print(f"The latest version in the store ({latest_store_version}) is older than the latest version in the buildinfo ({latest_buildinfo_version})")
        sys.exit(0)
    elif result == 2:
        print(f"The latest version in the store ({latest_store_version}) is newer than the latest version in the buildinfo ({latest_buildinfo_version})")
        sys.exit(1)
    else:
        print(f"The latest version in the store ({latest_store_version}) is the same as the latest version in the buildinfo ({latest_buildinfo_version})")
        sys.exit(1)

if __name__ == "__main__":
    main()
