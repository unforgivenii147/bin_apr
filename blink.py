#!/data/data/com.termux/files/usr/bin/python
import os
import sys
from pathlib import Path

from loguru import logger


def get_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            fullpath = Path(root) / file
            if fullpath.is_dir():
                continue
            if ".git" in fullpath.parts:
                continue
            if fullpath.is_symlink():
                yield fullpath


if __name__ == "__main__":
    cwd = Path.cwd()
    bcount = 0
    for path in get_files(cwd):
        if path.is_symlink() and not path.exists():
            try:
                path.unlink()
                bcount += 1
                logger.info(f"{path.relative_to(cwd)}")
            except Exception as e:
                logger.info(f"Error deleting {path}: {e}")
    if not bcount:
        logger.info("no broken link found.")
        sys.exit(0)
    logger.info(f"{bcount} broken link removed.")
