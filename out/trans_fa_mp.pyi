from _typeshed import Incomplete

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from deep_translator import GoogleTranslator
from loguru import logger

INPUT_FILE: Literal["words.txt"] = "words.txt"
OUTPUT_FILE: Literal["dic_mp.json"] = "dic_mp.json"
MAX_WORKERS: Literal[16] = 16

def translate_word(word: Incomplete) -> Incomplete: ...
def main() -> Incomplete: ...
