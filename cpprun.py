import sys
from glob import glob
from pathlib import Path
from dh import runcmd


if __name__ == "__main__":
    args = sys.argv[1:]

    if args:
        for arg in args:
            if "*" in arg:
                p = glob_glob(arg)
                print(p)
#    for f in files:
#        cmd=f"g++ -std=c++17 -Wall -Wextra -O2 "$file" -o "$exe" && ./"$exe""
