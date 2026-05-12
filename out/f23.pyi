from _typeshed import Incomplete

import argparse
import re
import shutil
from pathlib import Path
from loguru import logger

PRINT_PATTERN: Pattern[str]
PRINT_BARE_PATTERN: Pattern[str]
EXCEPT_PATTERN: Pattern[str]

def fix_py2_to_py3_all(line: Incomplete) -> Incomplete: ...
def fix_print_statements(text: Incomplete) -> Incomplete: ...
def apply_all_fixes(text: Incomplete) -> Incomplete: ...

changed_files: Incomplete
error_files: Incomplete

def process_file(path: Path, force: Incomplete = False, apply_all: Incomplete = False) -> None: ...
def scan_and_fix(root: Path, force: Incomplete, apply_all: Incomplete) -> None: ...
