#!/data/data/com.termux/files/usr/bin/python
"""
Sort lines of a file by line length (shortest first).
Supports large files via mmap (>5 MB).
Includes benchmarking for multiple approaches.
"""

import sys
import os
import mmap
import time
import tracemalloc
from pathlib import Path
from typing import List, Tuple, Optional
import functools

MMAP_THRESHOLD = 50 * 1024 * 1024


def read_lines_standard(path: Path) -> List[str]:
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    if not lines[-1].endswith(("\n", "\r\n", "\r")) and data.endswith(b"\n"):
        lines.append("")
    return lines


def read_lines_mmap(path: Path) -> List[str]:
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        with mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ) as mm:
            text = mm[:].decode("utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    if not lines[-1].endswith(("\n", "\r\n", "\r")) and size > 0 and text.endswith("\n"):
        lines.append("")
    return lines


def sort_by_length(lines: List[str]) -> List[str]:
    return sorted(lines, key=len)


def write_lines(path: Path, lines: List[str]) -> None:
    with open(path, "wb") as f:
        for line in lines:
            f.write(line.encode("utf-8"))


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
    if use_mmap:
        lines = read_lines_mmap(path)
    else:
        lines = read_lines_standard(path)
    sorted_lines = sort_by_length(lines)
    write_lines(path, sorted_lines)
    print(f"\n✅ Sorted {len(sorted_lines)} lines by length → saved to '{path}'")


if __name__ == "__main__":
    main()
