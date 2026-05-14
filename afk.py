#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from dh import cprint, fsz, get_pyfiles, mpf3
from autoflake import fix_code


def process_file(fp):
    code = fp.read_text(encoding="utf-8")
    result = fix_code(code, remove_all_unused_imports=True, additional_imports=["loguru"])
    diff_size = len(code) - len(result)
    if diff_size:
        print(f"{fp.name} ", end="")
        cprint(f"diff : {fsz(diff_size)}", "cyan")
        fp.write_text(result, encoding="utf-8")
    else:
        print(f"{fp.name} no change")


if __name__ == "__main__":
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else get_pyfiles(cwd)

    mpf3(process_file, files)
