import argparse
import os

from data import get_known_versions, load_version_file, save_version_file
from download import fetch_version_info, fetch_versions

parser = argparse.ArgumentParser(description='Minecraft Server Protocol Version Fetcher')
parser.add_argument(
    "type",
    choices=["release", "snapshot"],
    help="Version Type (release or snapshot)."
)


def append_to_github_file(env_var: str, line: str):
    """
    Appends a line to a GitHub Actions file like GITHUB_OUTPUT. Does nothing outside of GitHub Actions.
    """
    file_path = os.environ.get(env_var)
    if not file_path:
        return

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{line}\n")


def run(version_type: str):
    version_data = load_version_file(version_type)
    known_versions = get_known_versions(version_data)
    versions = fetch_versions(version_type)
    missing_versions = {version: url for version, url in versions.items() if version not in known_versions}

    print(f"Found {len(versions)} minecraft versions.")
    print(f"Missing minecraft versions: {list(missing_versions)}")

    if not missing_versions:
        return

    new_version_data = []
    for version, url in missing_versions.items():
        print(f"Downloading minecraft version {version}...")
        new_version_data.append(fetch_version_info(version, url))

    save_version_file(version_type, new_version_data + version_data)

    added_versions = ",".join(missing_versions)
    append_to_github_file("GITHUB_OUTPUT", f"added_versions={added_versions}")
    append_to_github_file("GITHUB_STEP_SUMMARY", f"Added {version_type} versions: {added_versions}")


if __name__ == "__main__":
    args = parser.parse_args()
    run(args.type)
