from _typeshed import Incomplete

import ast
import importlib.metadata
import importlib.util
import sys
from pathlib import Path
from dh import is_python_file
from loguru import logger

PACKAGE_MAPPING: dict[str, str]

def get_imports_from_file(file_path: Incomplete) -> Incomplete: ...
def check_status(module_name: Incomplete) -> Incomplete: ...
def main() -> Incomplete: ...
