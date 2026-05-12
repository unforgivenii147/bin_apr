from _typeshed import Incomplete

import sys
import tarfile
import zipfile
from pathlib import Path
from dh import get_files, unique_path
from loguru import logger

def whl_to_tar_xz(whl_path: Path) -> Incomplete: ...
def main() -> Incomplete: ...
