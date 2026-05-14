#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <file_a> <file_b>", file=sys.stderr)
        sys.exit(1)

    file_a = Path(sys.argv[1])
    file_b = Path(sys.argv[2])

    if not file_a.is_file():
        print(f"Error: {file_a} does not exist or is not a file", file=sys.stderr)
        sys.exit(1)

    if not file_b.is_file():
        print(f"Error: {file_b} does not exist or is not a file", file=sys.stderr)
        sys.exit(1)

    with file_b.open("r", encoding="utf-8") as fb:
        b_lines = {line.rstrip("\n") for line in fb}

    with file_a.open("r", encoding="utf-8") as fa:
        a_lines = fa.readlines()

    kept_lines = []
    for line in a_lines:
        if line.rstrip("\n") not in b_lines:
            kept_lines.append(line)

    # update a.txt in place safely
    tmp_path = file_a.with_suffix(file_a.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as tmp:
        tmp.writelines(kept_lines)

    tmp_path.replace(file_a)


if __name__ == "__main__":
    main()
