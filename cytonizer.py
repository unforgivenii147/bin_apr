#!/data/data/com.termux/files/usr/bin/python


from utils import (
    START_DIR,
    NUM_PROCESSES,
    main,
    main,
    process_file,
    main,
    main,
    main,
    main,
    main,
    main,
    main,
    main,
)
#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path
import os
from dh import get_files, mpf3

START_DIR = Path.cwd()
NUM_PROCESSES = 4


def process_file(path):
    pardir = path.parent
    os.chdir(pardir)
    os.system(f"cythonize {path.name}")


#    cmd=["cythonize",str(path)]
#    ret,txt,err = runcmd(cmd,show_output=True)
#    print(ret)
#    print(txt)
#    print(err)


def main():
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = []
    if args:
        for arg in args:
            p = Path(arg)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                files.extend(get_files(p, extensions=[".pyx"]))
    else:
        files = get_files(root_dir, extensions=[".pyx"])
    _ = mpf3(process_file, files)


if __name__ == "__main__":
    sys.exit(main())
