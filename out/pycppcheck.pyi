import sys
from collections import deque
from multiprocessing import get_context
from pathlib import Path
from dh import get_files, run_command
from termcolor import cprint

c_files: set[str]
cpp_files: set[str]

def validate_cpp(path: Path) -> tuple[bool, str]: ...
