#!/data/data/com.termux/files/usr/bin/python
import subprocess
from pathlib import Path
from dh import get_files, runcmd, mpf, gsz, fsz
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
            cprint(f" NO CHANGE", "green")
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
