#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines(keepends=False)
    if not lines:
        return False
    nl = []
    for line in lines:
        if not line.startswith("from utils"):
            nl.append(line)
    path.write_text("\n".join(nl) + "\n", encoding="utf-8")
    return True


def main() -> None:
    fixed = 0
    cwd = Path.cwd()
    for file in cwd.rglob("*.py"):
        if fix_file(file):
            fixed += 1
            print(f"Updated: {file}")
    print(f"\nDone. Updated {fixed} files.")


if __name__ == "__main__":
    main()
