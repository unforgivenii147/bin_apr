#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from loguru import logger

if __name__ == "__main__":
    try:
        with Path(sys.argv[1]).open(encoding="utf-8", errors="ignore") as f:
            logger.info(f.read(4096))
    except:
        with Path(sys.argv[1]).open("rb") as f:
            logger.info(f.read(4096))
