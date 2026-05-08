#!/data/data/com.termux/files/usr/bin/python
import glob
import os
import sys
from pathlib import Path
from runpy import run_module
from rapidfuzz import fuzz
from pip._internal.cli.main import main as pip_main

whl_dir = "/sdcard/whl"
cwd = Path(whl_dir)


def install(packages: list[str]):
    args = ["install", "--no-compile", "--no-dependencies", *packages]
    return pip_main(args)


def pkg_name(txt):
    indx = txt.index("-")
    slash = txt.rfind("/")
    return txt[slash + 1 : indx]


def install_whl_by_wildcard(pkg):
    whl = {pkg_name(str(p)): str(p) for p in cwd.glob("*.whl")}
    wheel_files = []
    for k, v in whl.items():
        pr = fuzz.partial_ratio(pkg, k)
        if pkg in k and pr > 95:
            wheel_files.append(v)
    if not wheel_files:
        print(f"No .whl files found matching '{pkg}*'")
        return
    try:
        res = install(wheel_files)
        if not res:
            for f in wheel_files:
                print(f"  - {Path(f).name}")
                Path(f).unlink()
    except:
        return


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pip_install.py <pkg_wildcard>")
        sys.exit(1)
    wildcard = sys.argv[1]
    install_whl_by_wildcard(wildcard)
