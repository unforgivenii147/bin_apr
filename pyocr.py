#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path
import cv2
import pytesseract
from loguru import logger

SUPPORTED_FORMATS = {
    ".png",
    ".bmp",
    ".tiff",
    ".webp",
    ".jpg",
    ".jpeg",
}


def extract_text(file_path: str) -> bool:
    path = Path(file_path)
    if not path.is_file() or path.suffix.lower() not in SUPPORTED_FORMATS:
        logger.info(f"Error: '{path.name}' is not a supported image file.")
        return False
    output_path = path.with_suffix(".txt")
    try:
        img = cv2.imread(str(path))
        if img is None:
            logger.info(f"Error: Could not read {path.name}")
            return False
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        logger.info(f"Processing '{path.name}'...")
        text = pytesseract.image_to_string(gray)
        if not text.strip():
            logger.info(f"Warning: No text detected in '{path.name}'.")
        Path(output_path).write_text(text, encoding="utf-8")
        logger.info(f"Success! Text saved to '{output_path.name}'")
        return True
    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        logger.info(f"Usage: {sys.argv[0]} <image_file>")
        sys.exit(1)
    if extract_text(sys.argv[1]):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
