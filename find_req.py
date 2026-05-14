#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path
from dh import cprint


def process_file(path, text):
    content = path.read_text().lower()
    target1 = "require-dist: " + text
    target2 = "provide-extra: " + text
    target3 = " " + text
    if target1 in content or target2 in content:
        print(path.parent.name)
    if target3 in content:
        cprint(path.parent.name)


if __name__ == "__main__":
    #    major, minor, _, _, _ = sys.version_info
    #    py_version = f"{major}{minor}"
    cwd = Path(f"/data/data/com.termux/files/usr/lib/python3.13/site-packages")
    target = sys.argv[1]
    for path in cwd.rglob("METADATA"):
        process_file(path, target)
