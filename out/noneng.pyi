from _typeshed import Incomplete

import os
from pathlib import Path
from dh import BIN_EXT, TXT_EXT, is_binary
from langdetect import DetectorFactory, detect
from langdetect.lang_detect_exception import LangDetectException
from loguru import logger

MAX_CHARS: Literal[5000] = 5000

def is_text_file(pth: Incomplete) -> Incomplete: ...
def contains_non_english(path: Incomplete) -> Incomplete: ...
def main() -> Incomplete: ...
