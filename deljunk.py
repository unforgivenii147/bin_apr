#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from dh import fsz, gsz, get_files

EMPTYIT = False
RMIT = True


def empty_it(pth) -> None:
    Path(pth).write_text("", encoding="utf-8")


def remove_it(fp) -> None:
    if not fp.is_symlink():
        fp.unlink()


def load_junk():
    with Path("/sdcard/junk").open(encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def main():
    cwd = Path.cwd()
    before = gsz(cwd)
    junk_files = load_junk()
    for path in get_files(cwd):
        if path.name in {".travis.yml", ".gitkeep", ".dirinfo", ".pyformat_cache.json", "simz.json"}:
            path.unlink()
            continue
        if any(path.name.lower() == junk for junk in junk_files) and path.exists():
            if RMIT:
                remove_it(path)
                print(path.relative_to(cwd))
                continue
            if EMPTYIT:
                empty_it(path)
                print(path.relative_to(cwd))
    difsize = before - gsz(cwd)
    print(f"{fsz(difsize)}")


if __name__ == "__main__":
    sys.exit(main())
