#!/data/data/com.termux/files/usr/bin/python
import json
from pathlib import Path
from deep_translator import GoogleTranslator
from loguru import logger

INPUT_FILE = "words.txt"
OUTPUT_FILE = "dic.json"


def translate_word(word):
    try:
        return GoogleTranslator(source="auto", target="en").translate(word)
    except Exception as e:
        logger.info(f"Error translating '{word}': {e}")
        return None


def main():
    translations = {}
    with Path(INPUT_FILE).open(encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    logger.info(f"Loaded {len(words)} Persian words")
    for w in words:
        eng = translate_word(w)
        if eng:
            translations[w] = eng
            logger.info(f"{w} → {eng}")
    with Path(OUTPUT_FILE).open("w", encoding="utf-8") as f:
        json.dump(
            translations,
            f,
            ensure_ascii=False,
            indent=2,
        )
    logger.info(f"\nSaved JSON dictionary to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
