#!/data/data/com.termux/files/usr/bin/python
"""
Compress top-level directories in the current directory recursively with tar,
remove originals, then compress remaining top-level files individually with py7zr.

Requirements:
  pip install py7zr

Notes:
- Uses pathlib for traversal.
- Top-level directories are archived as .tar with maximum compression via py7zr.
- After successful archive creation, the original directory/file is removed.
- Errors are logged and processing continues.
- Uses multiprocessing to speed up per-item compression.
"""

from __future__ import annotations

import logging
import multiprocessing as mp
import shutil
import tarfile
from pathlib import Path
from typing import Iterable, Tuple

import py7zr
from dh import fsz, gsz

# ----------------------------
# Configuration
# ----------------------------

ROOT = Path.cwd()
LOG_FILE = ROOT / "compress.log"

# py7zr compression preset: higher is slower but better compression.
# Valid range is typically 0..9, where 9 is max compression.
PY7ZR_PRESET = 9


# ----------------------------
# Logging
# ----------------------------


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(processName)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


# ----------------------------
# Helpers
# ----------------------------


def is_top_level_entry(path: Path) -> bool:
    """Only operate on entries directly under ROOT."""
    try:
        return path.parent.resolve() == ROOT.resolve()
    except Exception:
        return path.parent == ROOT


def iter_top_level_dirs(root: Path) -> Iterable[Path]:
    for p in root.iterdir():
        if p.is_dir() and not p.is_symlink():
            yield p


def iter_top_level_files(root: Path) -> Iterable[Path]:
    for p in root.iterdir():
        if p.is_file() and not p.is_symlink() and not p.suffix in {".7z", ".xz", ".br", ".zst", ".gz", ".zip", ".whl"}:
            yield p


def safe_remove(path: Path) -> None:
    """Remove file or directory, logging any error."""
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    except Exception:
        logging.exception("Failed to remove %s", path)


# ----------------------------
# Compression functions
# ----------------------------


def compress_dir_to_tar_then_7z(dir_path: str) -> Tuple[str, bool, str]:
    """
    Compress a directory to .tar first, then compress that tar to .7z,
    and remove the original directory if successful.

    Returns: (source, success, message)
    """
    src = Path(dir_path)
    tar_path = src.with_suffix(".tar")
    out_path = src.with_suffix(".tar.7z")

    try:
        # 1) Create tar archive
        if tar_path.exists():
            tar_path.unlink()

        with tarfile.open(tar_path, mode="w") as tar:
            tar.add(src, arcname=src.name)

        # 2) Compress tar with py7zr (maximum compression)
        if out_path.exists():
            out_path.unlink()

        with py7zr.SevenZipFile(
            out_path, mode="w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": PY7ZR_PRESET}]
        ) as archive:
            archive.write(tar_path, arcname=tar_path.name)

        # 3) Remove originals
        shutil.rmtree(src)
        tar_path.unlink(missing_ok=True)

        return (str(src), True, f"Compressed directory -> {out_path.name}")

    except Exception as e:
        logging.exception("Error compressing directory %s", src)
        # Cleanup partially created artifacts, but don't fail the whole run
        try:
            if tar_path.exists():
                tar_path.unlink()
        except Exception:
            logging.exception("Failed to cleanup tar %s", tar_path)

        return (str(src), False, f"{type(e).__name__}: {e}")


def compress_file_to_7z(file_path: str) -> Tuple[str, bool, str]:
    """
    Compress a single file to .7z with maximum compression,
    and remove the original file if successful.

    Returns: (source, success, message)
    """
    src = Path(file_path)
    out_path = src.with_suffix(src.suffix + ".7z") if src.suffix else src.with_name(src.name + ".7z")

    try:
        if out_path.exists():
            out_path.unlink()

        with py7zr.SevenZipFile(
            out_path, mode="w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": PY7ZR_PRESET}]
        ) as archive:
            archive.write(src, arcname=src.name)

        src.unlink()
        return (str(src), True, f"Compressed file -> {out_path.name}")

    except Exception as e:
        logging.exception("Error compressing file %s", src)
        try:
            if out_path.exists():
                out_path.unlink()
        except Exception:
            logging.exception("Failed to cleanup archive %s", out_path)

        return (str(src), False, f"{type(e).__name__}: {e}")


# ----------------------------
# Main workflow
# ----------------------------


def main() -> None:
    setup_logging()
    logging.info("Starting compression in %s", ROOT)

    # Step 1: Compress all top-level dirs first (in parallel)
    dirs = [p for p in iter_top_level_dirs(ROOT)]
    if dirs:
        logging.info("Found %d top-level directories", len(dirs))
        with mp.Pool(processes=4) as pool:
            for src, ok, msg in pool.imap_unordered(compress_dir_to_tar_then_7z, map(str, dirs)):
                if ok:
                    logging.info("%s: %s", src, msg)
                else:
                    logging.error("%s: %s", src, msg)
    else:
        logging.info("No top-level directories found")

    # Step 2: Compress remaining top-level files individually (in parallel)
    files = [p for p in iter_top_level_files(ROOT)]
    if files:
        logging.info("Found %d top-level files", len(files))
        with mp.Pool(processes=max(1, mp.cpu_count() - 1)) as pool:
            for src, ok, msg in pool.imap_unordered(compress_file_to_7z, map(str, files)):
                if ok:
                    logging.info("%s: %s", src, msg)
                else:
                    logging.error("%s: %s", src, msg)
    else:
        logging.info("No top-level files found")

    logging.info("Done.")


if __name__ == "__main__":
    cwd = Path.cwd()
    before = gsz(cwd)
    mp.freeze_support()
    main()
    after = gsz(cwd)
    diff_size = before - after
    if not diff_size:
        print("no change")
    print(f"space freed : {fsz(diff_size)}")
