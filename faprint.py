#!/data/data/com.termux/files/usr/bin/python
from print_persian import print_persian as pp
import sys
from pathlib import Path

if __name__ == "__main__":
    fn = Path(sys.argv[1])
    text = fn.read_text(encoding="utf8")
    pp(text)
