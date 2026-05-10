#!/data/data/com.termux/files/usr/bin/python

import mmap
import os
import sys
from pathlib import Path
from typing import List
from loguru import logger

MMAP_THRESHOLD = 50 * 1024 * 1024


def read_lines_standard(path: Path) -> list[str]:
    data = Path(path).read_bytes()
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    if not lines[-1].endswith(("\n", "\r\n", "\r")) and data.endswith(b"\n"):
        lines.append("")
    return lines


def read_lines_mmap(path: Path) -> list[str]:
    size = Path(path).stat().st_size
    with Path(path).open("rb") as f, mmap.mmap(f.fileno(),
                                               size,
                                               access=mmap.ACCESS_READ) as mm:
        text = mm[:].decode("utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    if not lines[-1].endswith(
        ("\n", "\r\n", "\r")) and size > 0 and text.endswith("\n"):
        lines.append("")
    return lines


def sort_by_length(lines: list[str]) -> list[str]:
    return sorted(lines, key=len)


def write_lines(path: Path, lines: list[str]) -> None:
    with Path(path).open("wb") as f:
        f.writelines((line.encode("utf-8") for line in lines))


def fsz(size: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(size) < 1024.0:
            return f"{size:3.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PiB"


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: File '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    size = path.stat().st_size
    use_mmap = size > MMAP_THRESHOLD
    lines = read_lines_mmap(path) if use_mmap else read_lines_standard(path)
    sorted_lines = sort_by_length(lines)
    write_lines(path, sorted_lines)
    print(f"\n✅ Sorted {len(sorted_lines)} lines by length → saved to '{path}'")


if __name__ == "__main__":
    main()
