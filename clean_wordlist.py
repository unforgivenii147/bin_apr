#!/data/data/com.termux/files/usr/bin/python
import sys
from collections import defaultdict

from dh import read_lines


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <wordlist.txt>", file=sys.stderr)
        sys.exit(1)

    fname = sys.argv[1]

    lines = read_lines(fname)

    similar = set()
    n = len(lines)

    # Move both lines that differ by exactly one character
    # (same length, same positions except one char)
    groups = defaultdict(list)
    for i, line in enumerate(lines):
        print(f"{i}/{n}")
        for pos in range(len(line)):
            key = (len(line), line[:pos] + "\0" + line[pos + 1 :], pos)
            groups[key].append(i)

    for idxs in groups.values():
        if len(idxs) >= 2:
            # mark all lines in this group as similar
            for i in idxs:
                similar.add(i)

    # Write similar lines to similar.txt
    with open("similar.txt", "w", encoding="utf-8") as f:
        for i in sorted(similar):
            f.write(lines[i] + "\n")

    # Rewrite original file in place without similar lines
    remaining = [line for i, line in enumerate(lines) if i not in similar]
    with open(fname, "w", encoding="utf-8") as f:
        for line in remaining:
            f.write(line + "\n")


if __name__ == "__main__":
    main()
