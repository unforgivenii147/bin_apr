#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path

from dh import DOC_TH1, cprint, fsz, gsz, mpf
from loguru import logger
from termcolor import cprint

N_JOBS = -1


def process_file(fp):
    data = fp.read_text(encoding="utf-8")
    lines = data.splitlines(keepends=False)
    nl = []
    removed = 0
    for line in lines:
        stripped = line.lstrip(" ").rstrip(" ").strip()
        if stripped.startswith(DOC_TH1) and stripped.endswith(DOC_TH1) and stripped != DOC_TH1 * 2:
            removed += 1
            continue
        nl.append(line)
    if removed:
        try:
            code = "\n".join(nl)
            _ = ast.parse(code)
            fp.write_text(code, encoding="utf8")
            return f"{fp.name} : OK"
        except:
            return f"{fp.name} : AST PARSE ERROR"
    else:
        return f"{fp.name} : NOCHANGE"


def main():
    root_dir = Path.cwd()
    before = gsz(root_dir)
    args = sys.argv[1:]
    files = []
    if args:
        for arg in args:
            p = Path(arg)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                files.extend(get_files(p, recursive=True))
    else:
        files = get_files(root_dir)
    results = mpf(process_file, files)
    for result in results:
        if result:
            logger.info(result)
    diffsize = before - gsz(root_dir)
    cprint(f"space change : {fsz(diffsize)}", "cyan")


if __name__ == "__main__":
    sys.exit(main())
