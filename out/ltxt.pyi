from _typeshed import Incomplete

import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dh import BIN_EXT
from loguru import logger
from tqdm import tqdm

EXCLUDED_EXTENSIONS: Incomplete

def process_file(filepath: Incomplete) -> Incomplete: ...
def collect_files_by_extension() -> Incomplete: ...
def collect_lines_for_extension(ext: Incomplete, files: Incomplete) -> Incomplete: ...
def main() -> Incomplete: ...
