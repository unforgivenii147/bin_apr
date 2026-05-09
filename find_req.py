#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from loguru import logger


def process_file(path, text):
    content = path.read_text()
    target = "Requires-Dist: " + text
    if target in content:
        print(path.parent.name)


if __name__ == "__main__":
    major, minor, _, _, _ = sys.version_info
    py_version = f"{major}{minor}"
    cwd = Path(f"/data/data/com.termux/files/usr/lib/python{py_version}/site-packages")
    target = sys.argv[1]
    for path in cwd.rglob("METADATA"):
        process_file(path, target)
