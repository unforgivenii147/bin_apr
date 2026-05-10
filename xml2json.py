#!/data/data/com.termux/files/usr/bin/python

import json
import sys
from collections import deque
from multiprocessing import get_context
from pathlib import Path
import xmltodict
from dh import cprint, get_files

MAX_QUEUE = 16
REMOVE_ORIG = True


def process_file(path):
    try:
        jsonpath = path.with_suffix(".json")
        cprint(f"{jsonpath} created.", "cyan")
        xml_content = path.read_text(encoding="utf-8", errors="ignore")
        with jsonpath.open("w") as f:
            data = xmltodict.parse(xml_content)
            json.dump(data, f, ensure_ascii=False, indent=2)
        if path.suffix == ".xml" and REMOVE_ORIG:
            path.unlink()
    except OSError as e:
        print(f"error {e}")


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else get_files(
        cwd, extensions=[".xml", ".svg"])
    with get_context("spawn").Pool(8) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()
    print("done.")


if __name__ == "__main__":
    main()
