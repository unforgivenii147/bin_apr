from _typeshed import Incomplete

import argparse
import sys
from pathlib import Path
from loguru import logger

EXCLUDED_NAMES: set[str]
EXCLUDED_PATH_COMPONENTS: set[str]

def is_excluded(path: Path, root_path: Path) -> bool: ...
def delete_empty_dirs_iterative(root: Path, dry_run: bool = False, verbose: bool = False) -> tuple[int, list[Path]]: ...
def main() -> Incomplete: ...
