#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from loguru import logger

from dh import fsz


def main():
    ext = sys.argv[1]
    total_size = 0
    count = 0
    cwd = Path.cwd()
    for f in cwd.rglob(f"*.{ext}"):
        total_size += f.stat().st_size
        count += 1
    logger.info(f"Total number of .{ext} files: {count}")
    logger.info(f"Total size of .{ext} files: {fsz(total_size)}")


if __name__ == "__main__":
    main()
