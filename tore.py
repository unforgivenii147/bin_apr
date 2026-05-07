import sys
from pathlib import Path
from time import time


if __name__ == "__main__":
    rdir = Path(sys.argv[1])
    print(time.now())
