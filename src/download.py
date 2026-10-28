import io
import json
import zipfile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

VERSION_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
TIMEOUT_SECONDS = 60

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
)))


def get(url: str) -> requests.Response:
    response = session.get(url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response


def fetch_versions(version_type: str) -> dict[str, str]:
    """
    Fetches all Minecraft versions of a specific type (release or snapshot) from the version manifest.

    Args:
        version_type (str): The type of versions to fetch ('release' or 'snapshot').

    Returns:
        dict: Version IDs (newest first) mapped to the URL of their version manifest.
    """
    manifest = get(VERSION_MANIFEST_URL).json()
    return {
        version["id"]: version["url"]
        for version in manifest["versions"]
        if version["type"] == version_type
    }


def fetch_version_info(version_id: str, url: str) -> dict:
    """
    Downloads the Minecraft client JAR and returns the content of the version.json in its root directory.
    Versions older than 18w47b don't contain a version.json, so only their name is returned.

    Args:
        version_id (str): The version ID of Minecraft.
        url (str): The URL of the version manifest.

    Returns:
        dict: The content of the version.json file or a fallback object with 'name'.
    """
    client_url = get(url).json()["downloads"]["client"]["url"]
    client_jar = io.BytesIO(get(client_url).content)

    with zipfile.ZipFile(client_jar) as jar_file:
        if "version.json" not in jar_file.namelist():
            print(f"version.json not found in client JAR of {version_id}")
            return {"name": version_id}

        with jar_file.open("version.json") as version_file:
            return json.load(version_file)
