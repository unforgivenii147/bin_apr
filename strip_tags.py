#!/data/data/com.termux/files/usr/bin/python
import re
import sys
from pathlib import Path

INPLACE = "-w" in sys.argv
from dh import read_lines

if __name__ == "__main__":
    fn = Path(sys.argv[1])
    content = fn.read_text(encoding="utf8")
    lines = content.splitlines(keepends=False)
    nl = []
    for line in lines:
        if "<:" in line or ">:" in line:
            continue
        text = re.sub("<[^>]*>", "", line)
        nl.append(text)
    new_content = "\n".join(nl)
    removed, _added = get_removed_lines(content, new_content)
    for k in removed:
        print(f" - {k}")
    if INPLACE:
        fn.write_text(new_content, encoding="utf8")
    print("file didnt updated.\n for update inplace rerun with -w arg")
