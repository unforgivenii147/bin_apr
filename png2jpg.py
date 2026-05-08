#!/data/data/com.termux/files/usr/bin/python
import os
import sys
from pathlib import Path
from loguru import logger
from PIL import Image

if len(sys.argv) != 2:
    logger.info("Usage: python convert_png_to_jpg.py <filename.png>")
    sys.exit(1)
fname = sys.argv[1]
if not Path(fname).is_file():
    logger.info(f"File {fname} does not exist.")
    sys.exit(1)
if not fname.lower().endswith(".png"):
    logger.info("File must be a PNG.")
    sys.exit(1)
img = Image.open(fname).convert("RGB")
jpg_fname = os.path.splitext(fname)[0] + ".jpg"
img.save(jpg_fname, "JPEG")
Path(fname).unlink()
print(f"Converted {fname} to {jpg_fname} and deleted the original PNG.")
