from _typeshed import Incomplete

import argparse
import re
import shutil
from pathlib import Path
from loguru import logger

LOCAL_FONT_BASE: Path
IMPORT_RE: Pattern[str]
URL_RE: Pattern[str]
RULE_RE: Pattern[str]
FONT_EXTS: set[str]
IMG_EXTS: set[str]

def detect_family(filename: str) -> Incomplete: ...
def copy_asset(src: Incomplete, assets_dir: Incomplete) -> Incomplete: ...
def rewrite_urls(css_text: Incomplete, css_dir: Incomplete, assets_dir: Incomplete) -> Incomplete: ...
def deduplicate_rules(css_text: Incomplete) -> Incomplete: ...
def process_css(file: Incomplete, assets_dir: Incomplete) -> Incomplete: ...
def main() -> Incomplete: ...
