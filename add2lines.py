#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import sys

if __name__ == "__main__":
    fn = sys.argv[1]
    newlines = []
    str_to_add = sys.argv[2]
    with Path(fn).open("r") as f:
        for line in f:
            ln = str_to_add + " " + line
            newlines.append(ln)
    with Path(fn).open("w") as fo:
        bbfo.writelines(newlines)
    print(f"{fn} updated")
