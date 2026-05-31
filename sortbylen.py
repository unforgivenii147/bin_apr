#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
from dh import read_lines


def sort_by_length(lines: list[str]) -> list[str]:
    return sorted(lines, key=len)


if __name__ == "__main__":
    import sys

    path = Path(sys.argv[1])
    lines = read_lines(path)
    sorted_lines = sort_by_length(lines)
    with path.open("wb") as f:
        f.writelines((line.encode("utf-8") for line in sorted_lines))
