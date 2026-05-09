#!/data/data/com.termux/files/usr/bin/python
import shutil
from pathlib import Path

from dh import is_binary
from loguru import logger


def main():
    current_dir = Path.cwd()
    binary_dir = current_dir / "binary"
    binary_dir.mkdir(exist_ok=True)
    files_moved = 0
    for f in current_dir.iterdir():
        if f.is_file() and is_binary(Path(f)):
            try:
                shutil.move(str(f), binary_dir / f.name)
                logger.info(f"Moved: {f.name} -> binary/{f.name}")
                files_moved += 1
            except Exception as e:
                logger.info(f"Failed to move {f.name}: {e}")
    if files_moved == 0:
        logger.info("No binary files found to move.")
    else:
        logger.info(f"Total binary files moved: {files_moved}")


if __name__ == "__main__":
    main()
