from _typeshed import Incomplete

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from deep_translator import GoogleTranslator
from dh import unique_path
from fastwalk import walk_files
from loguru import logger
from tqdm import tqdm

DIRECTORY: Literal["."] = "."
non_english_pattern: Pattern[str]

def is_english(text: Incomplete) -> Incomplete: ...

translation_cache: Incomplete

def translate_name(name: Incomplete) -> Incomplete: ...
def rename_files(directory: Incomplete) -> Incomplete: ...
