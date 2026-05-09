#!/data/data/com.termux/files/usr/bin/python
import json
import sys
import time

import requests
from dh import get_installed_packages
from loguru import logger
from packaging.version import InvalidVersion, Version


def check_package_on_pypi(package_name: str, current_version: str) -> str | None:
    try:
        time.sleep(0.01)
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
        if response.status_code == 404:
            return None
        return None
    except requests.exceptions.RequestException as e:
        logger.info(f"  ⚠️  Error checking {package_name}: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        logger.info(f"  ⚠️  Error parsing response for {package_name}: {e}")
        return None


def compare_versions(current: str, latest: str) -> str:
    try:
        current_v = Version(current)
        latest_v = Version(latest)
        if current_v < latest_v:
            return "update"
        if current_v > latest_v:
            return "newer"  # Curren return "current"
    except InvalidVersion:
        if current == latest:
            return "current"
        if current < latest:
            return "update"
        return "newer"


def is_venv() -> bool:
    return hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)


def main() -> None:
    if not is_venv():
        logger.info("⚠️  Warning: Not running in a virtual environment!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            logger.info("Exiting.")
            return
    logger.info("📦 Checking for package updates on PyPI...")
    logger.info("(Results will appear as each package is checked)\n")
    installed = get_installed_packages()
    total_packages = len(installed)
    logger.info(f"Processing {total_packages} packages:\n")
    updates_found = []
    errors = []
    up_to_date = 0
    for i, (
        package,
        current_version,
    ) in enumerate(sorted(installed.items()), 1):
        progress = f"[{i:3d}/{total_packages:3d}]"
        latest_version = check_package_on_pypi(package.lower(), current_version)
        if latest_version is None:
            logger.info(f"{progress} {package:<30} : ⚠️  not found on PyPI")
            errors.append(package)
            continue
        status = compare_versions(current_version, latest_version)
        if status == "update":
            logger.info(f"{progress} {package:<30} : 📦 update available from {current_version} to {latest_version}")
            updates_found.append(
                (
                    package,
                    current_version,
                    latest_version,
                )
            )
        elif status == "newer":
            logger.info(
                f"{progress} {package:<30} : ⚠️  current version ({current_version}) is newer than PyPI ({latest_version})",
            )
            errors.append(package)
        else:
            logger.info(f"{progress} {package:<30} : ✅ already latest version ({current_version})")
            up_to_date += 1
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total packages checked: {total_packages}")
    logger.info(f"✅ Up to date: {up_to_date}")
    logger.info(f"📦 Updates available: {len(updates_found)}")
    logger.info(f"⚠️  Errors/Not found: {len(errors)}")
    if updates_found:
        logger.info("\n" + "=" * 60)
        logger.info("PACKAGES TO UPDATE")
        logger.info("=" * 60)
        for (
            package,
            current,
            latest,
        ) in updates_found:
            logger.info(f"  {package:<30} {current} -> {latest}")
        logger.info("\n💡 To upgrade all packages, run:")
        packages_to_upgrade = [p[0] for p in updates_found]
        logger.info(f"   python -m pip install --upgrade {' '.join(packages_to_upgrade)}")
        logger.info("\n💡 To upgrade a specific package, run:")
        logger.info("   python -m pip install --upgrade <package-name>")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n❌ Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.info(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
