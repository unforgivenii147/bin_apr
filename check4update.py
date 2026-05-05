#!/data/data/com.termux/files/usr/bin/python
import json
from pathlib import Path
from importlib import metadata

import requests
from loguru import logger

logger.add("/sdcard/updatable.log")


def get_latest_version(pkg_name):
    """Query PyPI for the latest version of a package."""
    url = f"https://pypi.org/pypi/{pkg_name}/json"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()["info"]["version"]
        return None
    except Exception:
        return None


def main():
    results = []
    upgradable = []

    installed_packages = {dist.metadata["Name"]: dist.version for dist in metadata.distributions()}

    for pkg, installed_version in installed_packages.items():
        latest_version = get_latest_version(pkg)
        logger.info(f"{pkg}: {installed_version} {latest_version}")
        entry = {"pkgname": pkg, "installed_version": installed_version, "latest_version": latest_version}

        results.append(entry)

        if latest_version and latest_version != installed_version:
            upgradable.append(f"{pkg}=={latest_version}")
            logger.info(f"{pkg}=={installed_version} | {latest_version}")

    # Save JSON summary
    with Path("updatable.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    # Save only upgradeable packages as requirements
    Path("requirements.txt").write_text("\n".join(upgradable), encoding="utf-8")

    print("Done.")
    print(f"Checked {len(installed_packages)} installed packages.")
    print(f"Upgradeable packages: {len(upgradable)}")


if __name__ == "__main__":
    main()
