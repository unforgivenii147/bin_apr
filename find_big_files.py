#!/data/data/com.termux/files/usr/bin/python


from utils import (
    main,
    fsz,
    main,
    cwd,
    process_file,
    main,
    fsz,
    main,
    main,
    THRESHOLD,
    main,
    main,
    fsz,
    main,
    main,
    main,
)
#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path

from dh import fsz, get_filez

THRESHOLD = 1024 * 1024
cwd = Path.cwd()


def process_file(fp, threshold=THRESHOLD) -> None:
    sz = fp.stat().st_size
    if sz > threshold:
        print(f"{fp.relative_to(cwd)} : {fsz(sz)}")


def main():
    threshold = int(sys.argv[1]) * 1024 * 1024 if len(sys.argv) > 1 else THRESHOLD
    for path in get_filez(cwd):
        if not path.is_symlink():
            process_file(path, threshold)


if __name__ == "__main__":
    sys.exit(main())
