#!/data/data/com.termux/files/usr/bin/python
import json
import sys
from pathlib import Path

from loguru import logger


def minify_json_file(path: Path, dry_run: bool = False) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except Exception as e:
        logger.info(f"[ERROR] Cannot read {path}: {e}")
        return False
    try:
        data = json.loads(original)
    except json.JSONDecodeError:
        logger.info(f"[SKIP] Invalid JSON: {path}")
        return False
    minified = json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    if original.strip() == minified:
        return False
    if dry_run:
        logger.info(f"[DRY] Would minify: {path}")
        return True
    try:
        path.write_text(minified, encoding="utf-8")
        logger.info(f"[OK] Minified: {path}")
        return True
    except Exception as e:
        logger.info(f"[ERROR] Cannot write {path}: {e}")
        return False


def main():
    root = Path.cwd()
    dry_run = "--dry" in sys.argv
    modified_count = 0
    total_count = 0
    for path in root.rglob("*.json"):
        if path.is_file():
            total_count += 1
            if minify_json_file(path, dry_run=dry_run):
                modified_count += 1
    logger.info("\n--- Summary ---")
    logger.info(f"Total JSON files found: {total_count}")
    logger.info(f"Files modified: {modified_count}")


if __name__ == "__main__":
    main()
