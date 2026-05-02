#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path
from dh import get_pyfiles, mpf3
from loguru import logger
from pbar import Pbar

cwd = Path.cwd()
err_dir = Path(f"{cwd}/error")
err_dir.mkdir(exist_ok=True)


def process_file(fp) -> None:
    #    logger.info(f"processing ... {fp.name}")
    content = fp.read_text(encoding="utf-8")
    try:
        ast.parse(content)
    except:
        newpath = err_dir / fp.name
        newpath = Path(newpath)
        ans = input(f"confirm copying {fp.name} to error dir?(y/n)")
        if ans.lower() == "y":
            newpath.write_text(content, encoding="utf-8")


#            fp.unlink()
def main():
    args = sys.argv[1:]
    files = [Path(f) for f in args] if args else get_pyfiles(cwd)
    with Pbar("...") as pbar:
        for f in pbar.wrap(files):
            process_file(f)


#    mpf3(process_file,files)
if __name__ == "__main__":
    sys.exit(main())
