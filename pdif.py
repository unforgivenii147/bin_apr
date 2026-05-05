#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

from loguru import logger


def compare_files(file1, file2):
    try:
        with (
            Path(file1).open("r", encoding="utf-8") as f1,
            Path(file2).open("r", encoding="utf-8") as f2,
        ):
            lines1 = f1.readlines()
            lines2 = f2.readlines()
    except FileNotFoundError as e:
        logger.info(f"Error: {e}")
        return
    lines1 = [line.rstrip("\n") for line in lines1]
    lines2 = [line.rstrip("\n") for line in lines2]
    diff_lines_1 = []
    diff_lines_2 = []
    common_count = 0
    for i, line in enumerate(lines1):
        if line not in lines2:
            diff_lines_1.append(i + 1)  # 1-based index
    for i, line in enumerate(lines2):
        if line not in lines1:
            diff_lines_2.append(i + 1)
    for line in lines1:
        if line in lines2:
            common_count += 1
    logger.info(f"{file1} : {len(lines1)}")
    logger.info(f"{file2} : {len(lines2)}")
    logger.info(f"common: {common_count}")
    logger.info(f"Number of different lines in File 1: {len(diff_lines_1)}")
    if diff_lines_1:
        logger.info(f"Line numbers: {diff_lines_1}")
    logger.info(f"Number of different lines in File 2: {len(diff_lines_2)}")
    if diff_lines_2:
        logger.info(f"Line numbers: {diff_lines_2}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python script.py <file1> <file2>")
        sys.exit(1)
    compare_files(sys.argv[1], sys.argv[2])
