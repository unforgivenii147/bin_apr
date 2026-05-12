from _typeshed import Incomplete

import ast
import multiprocessing
import operator
import os
from pathlib import Path
import tree_sitter_python as tspython
from loguru import logger
from tree_sitter import Language, Parser, Query, QueryCursor

PY_LANGUAGE: Incomplete
parser: Incomplete
QUERY_STRING: Incomplete = "\n(comment) @comment\n(block\n  . (expression_statement\n    (string)) @docstring)\n(module\n  . (expression_statement\n    (string)) @docstring)\n"

def should_preserve_comment(content: Incomplete) -> Incomplete: ...
def strip_file(file_path: Incomplete) -> Incomplete: ...
def main() -> Incomplete: ...
