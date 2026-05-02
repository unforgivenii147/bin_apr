#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
from dh import get_files, gext, mpf, gsz, fsz
from rjsmin import jsmin
from termcolor import cprint


def process_file(path) -> str:
    before = gsz(path)
    print(f"{path.name}", end=" | ")
    after = before
    try:
        ext = gext(path)
        content = path.read_text(encoding="utf-8")
        if ext in {".js", ".min.js"}:
            minified = jsmin(content)
            after = len(minified)
        diff_size = len(content) - after
        if not diff_size:
            cprint(f"NO CHANGE", "green")
            return
        path.write_text(minified, encoding="utf-8")
        after = gsz(path)
        diff_size = before - after
        if diff_size > 0:
            reduction = ((before - after) / before) * 100
            cprint(f"- {fsz(diff_size)} | reduction : {reduction:.3f}%", "cyan")
            return
        if diff_size < 0:
            expantion = ((after - before) / after) * 100
            cprint(f"+ {fsz(diff_size)} | expantion : {expantion:.3f}%", "yellow")
            return
    except Exception as e:
        return f"{path}: {e}"


def main() -> None:
    cwd = Path.cwd()
    files = get_files(cwd, extensions=[".js", ".min.js"])
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    print(f"Found {len(files)} files. Starting multiprocessing...")
    mpf(process_file, files)


if __name__ == "__main__":
    main()
