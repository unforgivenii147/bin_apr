#!/data/data/com.termux/files/usr/bin/python
import json
import os
from pathlib import Path

from loguru import logger


def rename_pypi_metadata_files():
    files = [f for f in os.listdir(".") if f.endswith(".json")]
    for filename in files:
        try:
            with Path(filename).open(encoding="utf-8") as f:
                data = json.load(f)
            pkg_name = None
            if "info" in data and "name" in data["info"]:
                pkg_name = data["info"]["name"]
            elif "name" in data:
                pkg_name = data["name"]
            if pkg_name:
                new_name = f"{pkg_name}.json"
                if filename == new_name:
                    logger.info(f"Skipping: {filename} is already correctly named.")
                    continue
                Path(filename).rename(new_name)
                logger.info(f"Renamed: {filename} -> {new_name}")
            else:
                logger.info(f"Warning: Could not find package name in {filename}")
        except json.JSONDecodeError:
            logger.info(f"Error: {filename} is not a valid JSON file.")
        except Exception as e:
            logger.info(f"An error occurred with {filename}: {e}")


if __name__ == "__main__":
    rename_pypi_metadata_files()
