#!/data/data/com.termux/files/usr/bin/python


from utils import (
    main,
    process_archive,
    main,
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
from pathlib import Path
from typing import Optional, List

import py7zr


# =========================
# Config
# =========================

BASE_DIR = Path.cwd()
LOG_FILE = BASE_DIR / "decompress.log"
MAX_WORKERS = max(1, mp.cpu_count() - 1)

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
# Helpers
# =========================


def iter_archives(base_dir: Path):
    """
    Yield top-level archives to decompress:
    - .tar files
    - .7z files
    """
    for p in base_dir.iterdir():
        if p.is_file() and p.suffix in {".tar", ".7z"}:
            yield p


def tar_extract_dir_for(archive_path: Path) -> Path:
    """
    For 'name.tar' extract to 'name/' in the same directory.
    """
    return archive_path.parent / archive_path.stem


def seven_zip_extract_dir_for(archive_path: Path) -> Path:
    """
    For 'name.7z' extract to 'name/' in the same directory.
    """
    return archive_path.parent / archive_path.stem


def safe_extract_tar(archive_path: Path, target_dir: Path) -> None:
    """
    Extract tar archive to target_dir.
    """
    logging.info("Extracting TAR: %s -> %s", archive_path, target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r") as tar:
        tar.extractall(path=target_dir)


def safe_extract_7z(archive_path: Path, target_dir: Path) -> None:
    """
    Extract 7z archive to target_dir.
    """
    logging.info("Extracting 7Z: %s -> %s", archive_path, target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with py7zr.SevenZipFile(archive_path, mode="r") as archive:
        archive.extractall(path=target_dir)


def remove_path(path: Path) -> None:
    """
    Remove a file or directory recursively using pathlib.
    """
    if path.is_file() or path.is_symlink():
        path.unlink(missing_ok=True)
        return

    if path.is_dir():
        for child in path.iterdir():
            remove_path(child)
        path.rmdir()


# =========================
# Result model
# =========================


class TaskResult:
    def __init__(self, src: str, dst: str, ok: bool, error: Optional[str] = None):
        self.src = src
        self.dst = dst
        self.ok = ok
        self.error = error


# =========================
# Workers
# =========================


def process_archive(archive_path: Path) -> TaskResult:
    """
    Decompress archive and remove the original archive only if extraction succeeds.
    """
    try:
        if archive_path.suffix == ".tar":
            target_dir = tar_extract_dir_for(archive_path)
            if target_dir.exists():
                raise FileExistsError(f"Target already exists: {target_dir}")
            safe_extract_tar(archive_path, target_dir)

        elif archive_path.suffix == ".7z":
            target_dir = seven_zip_extract_dir_for(archive_path)
            if target_dir.exists():
                raise FileExistsError(f"Target already exists: {target_dir}")
            safe_extract_7z(archive_path, target_dir)

        else:
            raise ValueError(f"Unsupported archive type: {archive_path.suffix}")

        remove_path(archive_path)
        return TaskResult(str(archive_path), str(target_dir), True)

    except Exception as e:
        logging.exception("Failed to decompress %s", archive_path)
        return TaskResult(str(archive_path), "", False, str(e))


# =========================
# Main
# =========================


def main() -> None:
    setup_logging()
    logging.info("Starting decompression in %s", BASE_DIR)
    logging.info("Workers: %d", MAX_WORKERS)

    archives = list(iter_archives(BASE_DIR))
    logging.info("Found %d archives", len(archives))

    results: List[TaskResult] = []

    if archives:
        with mp.Pool(processes=min(MAX_WORKERS, len(archives))) as pool:
            results.extend(pool.map(process_archive, archives))

    success = sum(1 for r in results if r.ok)
    fail = len(results) - success

    logging.info("Completed. success=%d fail=%d", success, fail)
    for r in results:
        if not r.ok:
            logging.error("FAILED: %s | %s", r.src, r.error)


if __name__ == "__main__":
    mp.freeze_support()
    main()
