#!/data/data/com.termux/files/usr/bin/python

from pathlib import Path
import sys
from dh import get_ipkgs, runcmd, STDLIB, mpf3


def process_pkg(pkg) -> None:
    cmd = ["pyright", "--createstub", str(pkg)]
    ret, _, _ = runcmd(cmd, show_output=True)
    if not ret:
        return True
    return False


def main():
    std_pkgs = list(STDLIB)
    mpf3(process_pkg, std_pkgs)
    pkgs = get_ipkgs()
    mpf3(process_pkg, pkgs)


if __name__ == "__main__":
    sys.exit(main())
