#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path
from dh import get_files
from loguru import logger
from pbar import Pbar
from PyPDF2 import PdfReader


def process_file(pdf_path: Path):
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        print(f"Error: Invalid PDF file path provided: {pdf_path}")
        return
    pdf_filename_base = pdf_path.stem
    output_folder = pdf_path.parent / pdf_filename_base
    try:
        output_folder.mkdir(parents=True, exist_ok=True)
        print(f"Saving page text files to: {output_folder}")
    except OSError as e:
        print(f"Error creating output directory {output_folder}: {e}")
        return
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error opening PDF file {pdf_path}: {e}")
        return
    num_pages = len(reader.pages)
    print(f"Processing PDF: {pdf_path.name} ({num_pages} pages)")
    for page_num in range(num_pages):
        try:
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                page_filename = f"{pdf_filename_base}_page_{page_num + 1}.txt"
                output_filepath = output_folder / page_filename
                with output_filepath.open("w", encoding="utf-8") as txt_file:
                    txt_file.write(text)
                print(f"Saved: {output_filepath.name}")
            else:
                print(f"Warning: No text extracted from page {page_num + 1}.")
        except Exception as e:
            print(f"Error processing page {page_num + 1}: {e}")


if __name__ == "__main__":
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else get_files(cwd, extensions=[".pdf", ".PDF"])
    with Pbar("...") as pbar:
        for f in pbar.wrap(files):
            process_file(f)
