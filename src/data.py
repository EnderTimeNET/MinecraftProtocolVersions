import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_file_path(version_type: str) -> Path:
    return PROJECT_ROOT / f"{version_type}.json"


def load_version_file(version_type: str) -> list[dict]:
    version_file = get_file_path(version_type)

    if not version_file.exists():
        return []

    with version_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_version_file(version_type: str, data: list[dict]):
    with get_file_path(version_type).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_known_versions(version_data: list[dict]) -> set[str]:
    """
    Collects all 'id' and 'name' values of the given version entries.
    Both are needed: old versions only have a 'name', and some IDs differ from the manifest
    (e.g. '18w47b / 4858f333d8d64653bf77854bc05fa1cb').

    Args:
        version_data (list): The version entries of a version file.

    Returns:
        set: All known version IDs and names.
    """
    known_versions = set()
    for version in version_data:
        known_versions.update(version[key] for key in ("id", "name") if key in version)
    return known_versions
