#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from dh import get_files
from loguru import logger


def main():
    cwd = Path.home()
    files = get_files(cwd, extensions=[".html", ".htm"])
    for f in files:
        if f.stat().st_size > 1024 * 1024:
            logger.info(f.relative_to(cwd))


if __name__ == "__main__":
    main()
