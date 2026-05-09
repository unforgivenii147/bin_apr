#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys
from dh import get_files, get_ipkgs, runcmd, STDLIB, mpf3


def process_pkg(pkg) -> None:
    cmd = ["pyright", "--createstub", str(pkg)]
    ret, _, _ = runcmd(cmd, show_output=False)
    if not ret:
        return True
    return False


def main():
    #    pkgs = sys.stdlib_module_names
    #    with Pbar("") as pbar:
    #        for f in pbar.wrap(pkgs):
    #            process_pkg(f)

    std_pkgs = list(STDLIB)
    mpf3(process_pkg, pkgs)

    pkgs = get_ipkgs()
    mpf3(process_pkg, pkgs)


if __name__ == "__main__":
    sys.exit(main())
