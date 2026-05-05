#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from loguru import logger

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.info("Usage: python count_chars_of_input_file.py <input_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    try:
        with Path(input_file).open(encoding="utf-8") as file:
            content = file.read()
            char_count = len(content)
            logger.info(f"Number of characters in '{input_file}': {char_count}")
    except FileNotFoundError:
        logger.info(f"Error: File '{input_file}' not found.")
        sys.exit(1)
