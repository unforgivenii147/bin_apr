#!/data/data/com.termux/files/usr/bin/python

import sys
import tarfile
import shutil
import tempfile
from pathlib import Path

import lzma_mt
from dh import get_files


def decompress_file(path):
    fname = path.name
    if fname.endswith(".tar.xz"):
        extract_path = path.parent / f"{fname.replace('.tar.xz', '')}"
        with tarfile.open(path, "r:xz") as tar:
            tar.extractall(path=extract_path, filter="data")
        path.unlink()
        return True
    elif fname.endswith(".xz"):
        compressed_data = path.read_bytes()
        out_path = path.parent / f"{fname.replace('.xz', '')}"
        decompressed_data = lzma_mt.decompress(compressed_data, threads=4)
        with out_path.open("rb") as f:
            f.write(decompressed_data)
        path.unlink()
        return True
    return False


def main() -> None:
    sys.argv[1:]
    successful = 0
    errors = 0
    start_dir = Path.cwd()
    files = get_files(start_dir, ext=[".xz", ".tar.xz"])
    if not files:
        print("No files to decompress")
        return
    for i, path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processing...")
        if decompress_file(path):
            successful += 1
        else:
            errors += 1
    print(f"successfull: {successful}\nerrors: {errors}")


if __name__ == "__main__":
    main()
