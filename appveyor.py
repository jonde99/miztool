import os
import requests
from urllib.parse import urlparse

API_BASE = "https://ci.appveyor.com/api"


def parse_project_url(project_url: str):
    """
    Extract account and project slug from:
    https://ci.appveyor.com/project/{account}/{project}
    """
    parsed = urlparse(project_url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 3 or parts[0] != "project":
        raise ValueError("Invalid AppVeyor project URL")

    return parts[1], parts[2]


def get_last_successful_build(account, project):
    """
    Returns (job_id, build_version)
    """
    url = f"{API_BASE}/projects/{account}/{project}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    build = data.get("build")
    if not build or build.get("status") != "success":
        raise RuntimeError("Latest build is not successful")

    job_id = build["jobs"][0]["jobId"]
    version = build["version"]

    return job_id, version


def download_latest_artifact(project_url, download_dir):
    account, project = parse_project_url(project_url)

    job_id, version = get_last_successful_build(account, project)

    artifacts_url = f"{API_BASE}/buildjobs/{job_id}/artifacts"
    r = requests.get(artifacts_url)
    r.raise_for_status()
    artifacts = r.json()

    if not artifacts:
        raise RuntimeError("No artifacts found in successful build")

    artifact_name = artifacts[0]["fileName"]

    download_url = f"{API_BASE}/buildjobs/{job_id}/artifacts/{artifact_name}"

    r = requests.get(download_url, stream=True)
    r.raise_for_status()

    os.makedirs(download_dir, exist_ok=True)
    out_path = os.path.join(download_dir, artifact_name)

    size = 0
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                size += len(chunk)

    return {
        "path": out_path,
        "version": version,
        "artifact": artifact_name,
        "bytes": size,
        "job_id": job_id,
    }


