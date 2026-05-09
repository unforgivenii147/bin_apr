#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

from dh import fsz, get_files, gsz, mpf, runcmd
from loguru import logger
from termcolor import cprint


def process_file(path):
    before = gsz(path)
    try:
        runcmd(
            ["svgo", str(path)],
            run_silently=True,
            show_output=False,
        )
        diff_size = before - gsz(path)
        print(f"{path.name}", end=" | ")
        if not diff_size:
            cprint(" NO CHANGE", "green")
        if diff_size < 0:
            cprint(f" - {fsz(diff_size)}", "cyan")
        if diff_size > 0:
            cprint(f" + {fsz(diff_size)}", "yellow")
        return True, path
    except:
        return False, path


def main():
    cwd = Path.cwd()
    files = get_files(cwd, extensions=[".svg"])
    mpf(process_file, files)


if __name__ == "__main__":
    main()
