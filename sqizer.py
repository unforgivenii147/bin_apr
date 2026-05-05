#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
import re

from loguru import logger


def compress_python_file(filepath):
    content = Path(filepath).read_text(encoding="utf-8")
    # Remove multiline strings (docstrings)
    # This regex handles """...""" and '''...''' and is careful about nested quotes
    content = re.sub(r'""".*?"""|\'\'\'.*?\'\'\'', "", content, flags=re.DOTALL)
    # Remove single-line comments
    content = re.sub(r"#.*", "", content)
    # Remove leading/trailing whitespace from each line and then remove empty lines
    lines = content.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    content = "\n".join(non_empty_lines)
    Path(filepath).write_text(content, encoding="utf-8")


def compress_python_files_in_directory(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            filepath = os.path.join(directory, filename)
            logger.info(f"Compressing {filepath}...")
            compress_python_file(filepath)
    logger.info("Compression complete.")


if __name__ == "__main__":
    # You can change the directory here if needed
    compress_python_files_in_directory(".")
