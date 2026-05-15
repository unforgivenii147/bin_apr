#!/data/data/com.termux/files/usr/bin/python


from utils import (
    main,
    main,
    process_file,
    main,
    main,
    main,
    BASE_DIR,
    main,
    MAX_WORKERS,
    MAX_WORKERS,
    main,
    main,
    setup_logging,
    MAX_WORKERS,
    main,
    main,
)

#!/data/data/com.termux/files/usr/bin/python
from __future__ import annotations

import logging
import multiprocessing as mp
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import py7zr


# =========================
# Config
# =========================

BASE_DIR = Path.cwd()
LOG_FILE = BASE_DIR / "compress.log"
SCRIPT_NAME = Path(__file__).name if "__file__" in globals() else None
MAX_WORKERS = max(1, mp.cpu_count() - 1)

# Compression preference order for py7zr
# Pick the strongest general-purpose option available.
PREFERRED_METHODS = ["LZMA2", "LZMA", "PPMd"]

# =========================
# Logging
# =========================


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(processName)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


# =========================
# Compression method selection
# =========================


def choose_best_py7zr_method():
    """
    Choose the strongest method available in the installed py7zr version.
    Preference is based on compression ratio first, not speed.
    """
    comp = getattr(py7zr, "compressor", None)
    if comp is None:
        raise RuntimeError("py7zr.compressor module not found")

    for name in PREFERRED_METHODS:
        if hasattr(comp, name):
            return getattr(comp, name)

    raise RuntimeError(f"No supported compression methods found. Tried: {', '.join(PREFERRED_METHODS)}")


BEST_METHOD = choose_best_py7zr_method()


# =========================
# Helpers
# =========================


def iter_top_level_entries(base_dir: Path):
    """
    Yield top-level files and directories in current directory,
    excluding the script and any generated archives/log file.
    """
    for p in base_dir.iterdir():
        if p.name == LOG_FILE.name:
            continue
        if SCRIPT_NAME and p.name == SCRIPT_NAME:
            continue
        if p.suffix in {".tar", ".7z", ".br", ".gz", ".xz", ".zip", ".whl"}:
            continue
        yield p


def dir_to_tar_path(src_dir: Path) -> Path:
    return src_dir.parent / f"{src_dir.name}.tar"


def file_to_7z_path(src_file: Path) -> Path:
    return src_file.parent / f"{src_file.name}.7z"


def safe_remove_path(path: Path) -> None:
    """
    Remove a file or directory tree recursively.
    Directory removal uses pathlib only.
    """
    if path.is_file() or path.is_symlink():
        path.unlink(missing_ok=True)
        return

    if path.is_dir():
        for child in path.iterdir():
            safe_remove_path(child)
        path.rmdir()


def create_tar_from_dir(src_dir: Path, tar_path: Path) -> None:
    """
    Create a .tar archive for a directory.
    Uses recursive contents preservation.
    """
    logging.info("Tar directory: %s -> %s", src_dir, tar_path)
    with tarfile.open(tar_path, "w") as tar:
        tar.add(src_dir, arcname=src_dir.name)


def compress_file_to_7z(src_file: Path, out_path: Path) -> None:
    """
    Compress a file to .7z with the best available py7zr method.
    """
    logging.info("Compress file: %s -> %s", src_file, out_path)

    # preset=9 is maximum for LZMA/LZMA2 in py7zr
    # for PPMd, preset may be ignored depending on backend/version
    with py7zr.SevenZipFile(
        out_path,
        mode="w",
        filters=[{"id": BEST_METHOD, "preset": 9}],
    ) as archive:
        archive.write(src_file, arcname=src_file.name)


# =========================
# Result model
# =========================


@dataclass
class TaskResult:
    src: str
    dst: str
    ok: bool
    error: Optional[str] = None


# =========================
# Workers
# =========================


def process_directory(src_dir: Path) -> TaskResult:
    """
    Compress top-level directory into .tar, then delete original.
    """
    tar_path = dir_to_tar_path(src_dir)
    try:
        if tar_path.exists():
            raise FileExistsError(f"Target already exists: {tar_path}")

        create_tar_from_dir(src_dir, tar_path)
        safe_remove_path(src_dir)
        return TaskResult(str(src_dir), str(tar_path), True)
    except Exception as e:
        logging.exception("Directory failed: %s", src_dir)
        return TaskResult(str(src_dir), str(tar_path), False, str(e))


def process_file(src_file: Path) -> TaskResult:
    """
    Compress top-level file into .7z, then delete original.
    """
    out_path = file_to_7z_path(src_file)
    try:
        if out_path.exists():
            raise FileExistsError(f"Target already exists: {out_path}")

        compress_file_to_7z(src_file, out_path)
        safe_remove_path(src_file)
        return TaskResult(str(src_file), str(out_path), True)
    except Exception as e:
        logging.exception("File failed: %s", src_file)
        return TaskResult(str(src_file), str(out_path), False, str(e))


# =========================
# Main
# =========================


def main() -> None:
    setup_logging()
    logging.info("Base dir: %s", BASE_DIR)
    logging.info("Workers: %d", MAX_WORKERS)
    logging.info("Best py7zr method: %s", BEST_METHOD)

    entries = list(iter_top_level_entries(BASE_DIR))
    dirs = [p for p in entries if p.is_dir()]
    files = [p for p in entries if p.is_file()]

    logging.info("Found %d dirs and %d files", len(dirs), len(files))

    results: List[TaskResult] = []

    # Phase 1: directories -> tar
    if dirs:
        with mp.Pool(processes=min(MAX_WORKERS, len(dirs))) as pool:
            results.extend(pool.map(process_directory, dirs))

    # Phase 2: files -> 7z
    if files:
        with mp.Pool(processes=min(MAX_WORKERS, len(files))) as pool:
            results.extend(pool.map(process_file, files))

    success = sum(1 for r in results if r.ok)
    fail = len(results) - success

    logging.info("Completed. success=%d fail=%d", success, fail)
    for r in results:
        if not r.ok:
            logging.error("FAILED: %s -> %s | %s", r.src, r.dst, r.error)


if __name__ == "__main__":
    mp.freeze_support()
    main()
