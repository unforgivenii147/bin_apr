#!/data/data/com.termux/files/usr/bin/python

import operator
import os
import re
from pathlib import Path
from dh import get_files
from packaging.version import Version


def cdeb(fp):
    name = fp.stem
    if "_" in name:
        indx = name.index("_")
        return name[:indx]
    else:
        return name


if __name__ == "__main__":
    cwd = Path.cwd()
    wheel_pattern = re.compile("(?P<name>.+)-(?P<version>\\d+(\\.\\d+)+).*\\.whl")
    deb_pattern = re.compile("(?P<name>.+)_(?P<version>\\d+(\\.\\d+)+).*\\.deb")
    files = get_files(cwd, extensions=[".metadata", ".whl", ".deb"])
    print(f"{len(files)} files found.")
    packages = {}
    seen = set()
    pkgs = []
    for f in files:
        match1 = wheel_pattern.match(f.name)
        match2 = deb_pattern.match(f.name)
        if not match1 and (not match2):
            continue
        if match1:
            name = match1.group("name")
            version = Version(match1.group("version"))
        if match2:
            name = match2.group("name")
            version = Version(match2.group("version"))
        if name not in packages:
            packages[name] = []
            packages[name].append((version, f))
    for name, versions in packages.items():
        versions.sort(reverse=True, key=operator.itemgetter(0))
        latest = versions[0]
        old = versions[1:]
        for _v, filename in old:
            Path(filename).unlink()
            print(f"{filename} removed")
