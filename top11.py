#!/data/data/com.termux/files/usr/bin/python
import operator
from pathlib import Path

from loguru import logger

from dhh import fsz, get_files

cwd = Path.cwd()


def get_sizes():
    return [(file_path.relative_to(cwd), file_path.stat().st_size) for file_path in get_files(cwd)]


def main() -> None:
    sizez = get_sizes()
    if not sizez:
        logger.info("No files found or unable to access directory.")
        return
    sizez.sort(key=operator.itemgetter(1), reverse=True)
    top_files = sizez[:10]
    logger.info("\n" + "=" * 60)
    logger.info(f"TOP 10 LARGEST FILES (in {Path.cwd()})")
    logger.info("=" * 60)
    if not top_files:
        logger.info("No files found.")
        return
    max_path_len = max(len(str(path)) for path, size in top_files)
    max_path_len = min(max_path_len, 80)
    logger.info(f"{'No.':<4} {'File Path':<{max_path_len}} {'Size':>12}")
    logger.info("-" * (max_path_len + 20))
    for i, (file_path, size) in enumerate(top_files, 1):
        path_str = str(file_path)
        if len(path_str) > max_path_len:
            path_str = "..." + path_str[-(max_path_len - 3) :]
        size_str = fsz(size)
        logger.info(f"{i:<4} {path_str:<{max_path_len}} {size_str:>12}")
    total_files = len(sizez)
    logger.info("-" * (max_path_len + 20))
    logger.info(f"Total files scanned: {total_files}")
    if total_files > 10:
        logger.info(f"Showing top 10 out of {total_files} files")


def m2() -> None:
    sizez = get_sizes()
    if not sizez:
        logger.info("No files found.")
        return
    sizez.sort(key=operator.itemgetter(1), reverse=True)
    top_files = sizez[:10]
    logger.info("\nTOP 10 LARGEST FILES (Detailed View)")
    logger.info("=" * 70)
    for i, (file_path, size) in enumerate(top_files, 1):
        size_str = fsz(size)
        logger.info(f"{i:2d}. {size_str:>10} - {file_path.relative_to(cwd)}")


if __name__ == "__main__":
    main()
