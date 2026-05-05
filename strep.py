#!/data/data/com.termux/files/usr/bin/python
import sys
from dh import runcmd, fsz
from pathlib import Path


if __name__ == "__main__":
    fn = Path(sys.argv[1])
    before = fn.stat().st_size
    ret, _, _ = runcmd(["strip", str(fn)], show_output=True)
    after = fn.stat().st_size
    dz = before - after
    if dz:
        print(f"{fn.name} : before/after -> {fsz(before)}/{fsz(after)}   {((before - after) / before) * 100:.1f}%")
    else:
        print(f"{fn.name} : no change")
