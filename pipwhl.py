#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger

LOCAL_MIRROR_URL = "https://mirror-pypi.runflare.com"


def download_file(url, dest_folder="."):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        filepath = os.path.join(dest_folder, filename)
        with Path(filepath).open("wb") as f:
            f.writelines(response.iter_content(chunk_size=8192))
        logger.info(f"Downloaded: {filename}")
        return filepath
    except requests.exceptions.RequestException as e:
        logger.info(f"Error downloading {url}: {e}")
        return None


def get_package_info_from_mirror(package_name):
    mirror_package_url = f"{LOCAL_MIRROR_URL}/{package_name}"
    logger.info(f"Fetching package info from mirror: {mirror_package_url}")
    try:
        response = requests.get(mirror_package_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        wheel_urls = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.endswith(".whl"):
                full_url = f"{LOCAL_MIRROR_URL}{href}" if href.startswith("/") else href
                wheel_urls.append(full_url)
        if not wheel_urls:
            logger.info(f"No .whl files found for {package_name} on the mirror.")
            return None
        logger.info(f"Found wheel URLs for {package_name}: {wheel_urls}")
        return wheel_urls[0]
    except requests.exceptions.RequestException as e:
        logger.info(f"Error fetching from mirror {mirror_package_url}: {e}")
        return None
    except Exception as e:
        logger.info(f"An unexpected error occurred while parsing mirror response: {e}")
        return None


def install_or_download(package_name):
    logger.info(f"Checking for package: {package_name}")
    wheel_url = get_package_info_from_mirror(package_name)
    if wheel_url:
        logger.info(f"Wheel found for {package_name} at {wheel_url}. Installing...")
        try:
            install_command = [sys.executable, "-m", "pip", "install", wheel_url]
            subprocess.run(install_command, check=True)
            logger.info(f"Successfully installed {package_name} from wheel.")
        except subprocess.CalledProcessError as e:
            logger.info(f"Error installing {package_name} from {wheel_url}: {e}")
            logger.info(
                f"Installation failed for {package_name}. Could not find a source archive fallback from mirror."
            )
    else:
        logger.info(f"No wheel found for {package_name} on the mirror.")
        logger.info("This script currently only handles wheel installations from the mirror.")
        logger.info(
            "If a source archive (.tar.gz or .zip) were available and desired, additional parsing logic would be needed."
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.info("Usage: python pip_wrapper.py <package_name1> [package_name2 ...]")
        sys.exit(1)
    packages_to_process = sys.argv[1:]
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.info("The 'beautifulsoup4' library is required. Please install it: pip install beautifulsoup4")
        sys.exit(1)
    for pkg in packages_to_process:
        install_or_download(pkg)
