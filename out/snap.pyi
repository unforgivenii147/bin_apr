from _typeshed import Incomplete

import mmap
import sys
from pathlib import Path
import brotlicffi
from dh import fsz, get_files, gsz
from joblib import Parallel, delayed
from loguru import logger
from termcolor import cprint

CHUNK_SIZE: int
QUALITY: Literal[5] = 5
N_JOBS: Literal[-1]

def compress_chunk(data: Incomplete, quality: Incomplete = ...) -> Incomplete: ...
def parallel_compress(in_path: Incomplete, out_path: Incomplete) -> Incomplete: ...
def process_file(fp: Incomplete) -> Incomplete: ...
def main() -> Incomplete: ...
