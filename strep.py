#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path
from dh import fsz, get_files, mpf3, runcmd


def process_file(fp):
    before = fp.stat().st_size
    ret, _, _ = runcmd(["strip", str(fp)], show_output=True)
    after = fp.stat().st_size
    if not after:
        return
    dz = before - after
    if dz:
        print(
            f"{fp.name} -> {fsz(before)}/{fsz(after)} | ratio: {(before - after) / before * 100:.1f}%"
        )
    else:
        print(f"{fp.name} : no change")


if __name__ == "__main__":
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else get_files(
        cwd, extensions=[".so", ".SO"])
    mpf3(process_file, files)
