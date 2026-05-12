from _typeshed import Incomplete

import sys
from pathlib import Path
from dh import cprint, fsz, get_files, gsz, mpf3, runcmd

START_DIR: Path
NUM_PROCESSES: Literal[4] = 4

def process_file(path: Incomplete) -> Incomplete: ...
def main() -> Incomplete: ...
