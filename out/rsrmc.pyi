from _typeshed import Incomplete

import sys
from pathlib import Path
import tree_sitter_rust
from dh import clean_blank_lines, fsz, gsz
from loguru import logger
from termcolor import cprint
from tree_sitter import Language, Parser

EXCLUDE_PREFIXES: tuple[Literal[b"#!/"]]
parser: Incomplete

def process_file(path: Path) -> None: ...
def collect_rs_files(root: Path) -> list[Path]: ...
def main() -> None: ...
