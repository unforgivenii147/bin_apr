#!/data/data/com.termux/files/usr/bin/python
import json
from pathlib import Path
from dh import get_files, mpf3


def process_file(fp):
    data = ""
    try:
        with fp.open("r", encoding="utf8") as f:
            data = json.load(f)
        with fp.open("w") as fo:
            json.dump(data, fo, ensure_ascii=False, indent=None)
        print(f"[OK] {fp.name}")
    except:
        print(f"[ERROR] {fp.name}")
        return


if __name__ == "__main__":
    cwd = Path.cwd()
    files = get_files(cwd, extensions=[".json"])
    if not files:
        print("no json files found")
        sys.exit(1)

    mpf3(process_file, files)
