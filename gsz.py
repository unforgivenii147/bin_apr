#!/data/data/com.termux/files/usr/bin/python
import re
import sys
import requests
from loguru import logger


def get_repo_size(input_str):
    if input_str.startswith("https://github.com/"):
        match = re.search(r"github\.com/([^/]+)/([^/]+)", input_str)
        if not match:
            logger.info("Invalid GitHub URL format.")
            return
        user, repo = match.groups()
    else:
        parts = input_str.split("/")
        if len(parts) != 2:
            logger.info("Invalid format. Use 'user/repo' or full URL.")
            return
        user, repo = parts
    url = f"https://api.github.com/repos/{user}/{repo}"
    try:
        response = requests.get(url)
        if response.status_code == 404:
            logger.info(f"Repository '{user}/{repo}' not found.")
            return
        response.raise_for_status()
        data = response.json()
        size_bytes = data.get("size", 0)
        size_mb = size_bytes / (1024 * 1024)
        logger.info(f"Repository: {user}/{repo}")
        logger.info(f"Size: {size_mb:.2f} MB")
    except requests.exceptions.RequestException as e:
        logger.info(f"Error fetching data: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.info("Usage: python get-repo-size <user/repo> or <https://github.com/user/repo>")
        sys.exit(1)
    get_repo_size(sys.argv[1])
