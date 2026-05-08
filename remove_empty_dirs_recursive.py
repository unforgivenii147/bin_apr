#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
from loguru import logger


def main():
    count = 0
    for dirpath, dirnames, filenames in os.walk(Path.cwd(), topdown=False):
        if not dirnames and not filenames:
            logger.info(f"removing empty dir: {dirpath}")
            Path(dirpath).rmdir()
            count += 1
    logger.info(f"total {count} empty dirs removed")


if __name__ == "__main__":
    main()
