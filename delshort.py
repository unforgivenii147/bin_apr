#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from dh import get_files, is_binary


def process_file(fp) -> None:
    if not fp.exists():
        return
    if fp.exists() and fp.stat().st_size < 50 and len(fp.read_text().splitlines()) < 3:
        fp.unlink()
        print(f"{fp.name} removed")
    if fp.exists() and len(fp.read_text().splitlines()) < 2 and fp.stat().st_size < 50:
        fp.unlink()
        print(f"{fp.name} removed")


def main() -> None:
    cwd = Path.cwd()
    files = get_files(cwd)
    for path in files:
        if not is_binary(path) and path.exists():
            process_file(path)
        else:
            print(f"{path.name} is binary")


if __name__ == "__main__":
    sys.exit(main())
