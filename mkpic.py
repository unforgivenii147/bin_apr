#!/data/data/com.termux/files/usr/bin/python
import compileall
import sys
from collections import deque
from multiprocessing import get_context
from pathlib import Path

from loguru import logger

from dhh import fsz, get_files, gsz

MAX_QUEUE = 4
REMOVE_ORIG = False


def process_file(fp):
    if not fp.exists():
        return False
    #    if fp.name=="site-packages" or "site-packages" in fp.parts:
    #        return None
    if ".git" in fp.parts:
        return None
    if fp.is_dir():
        for f in fp.rglob("*.py"):
            process_file(f)
    if fp.is_file() and not fp.is_symlink():
        pyc_file = fp.with_suffix(".pyc")
        if pyc_file.exists():
            return False
        compileall.compile_file(fp, legacy=True, optimize=2)

        if REMOVE_ORIG:
            fp.unlink()
        return True
    return False


def main():
    cwd = Path.cwd()
    before = gsz(cwd)
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".py"])
    #    files = [p for p in cwd.glob("*") if not "site-packages" in p.parts]
    with get_context("spawn").Pool(4) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file, (f,)))
            if len(pending) > MAX_QUEUE:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


#    diff_size = before - gsz(cwd)
#    logger.info(f"space changed : {fsz(diff_size)}")

if __name__ == "__main__":
    main()
