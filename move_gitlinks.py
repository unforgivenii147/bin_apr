#!/data/data/com.termux/files/usr/bin/python


#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys


if __name__ == "__main__":
    fn = Path(sys.argv[1])
    lines = fn.read_text(encoding="utf-8").splitlines(keepends=False)
    nl = []
    gl = []
    for line in lines:
        if "github.com" in line:
            gl.append(line)
        else:
            nl.append(line)
    with fn.open("w", encoding="utf8") as fo:
        for k in nl:
            fo.write(f"{k}\n")
    if gl:
        gpath = Path("gitlinks")
        with gpath.open("a", encoding="utf8") as fg:
            for x in gl:
                fg.write(f"{x}\n")
    else:
        print("no git link")
