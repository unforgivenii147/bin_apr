#!/data/data/com.termux/files/usr/bin/python
import sys
from multiprocessing import get_context
from pathlib import Path
from dh import is_binary
from pbar import Pbar
from dhh import fsz, get_files, gsz, mpf3, run_command

cwd = Path.cwd()
outfile = cwd / "all_strings.txt"


def process_file(fp):
    if not fp.exists() or not is_binary(fp):
        return
    cmd = f"strings {fp!s}"
    _code, txt, _err = run_command(cmd)
    with Path(outfile).open("a", encoding="utf-8") as f:
        f.write(f"\n# filename : {fp.stem}\n{txt}\n")
    return


def main():
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(cwd)
    with Pbar("") as pbar:
        for f in pbar.wrap(files):
            process_file(f)


if __name__ == "__main__":
    sys.exit(main())
