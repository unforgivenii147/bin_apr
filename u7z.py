    DIRECTORY,
    CHUNK_SIZE,
    non_english_pattern,
    split_into_chunks,
    EXCLUDE_DIRS,
    read_file,
    extract_words,
    START_DIR,
    NUM_PROCESSES,
    main,
    random_key,
    decrypt_file,
    fetch_content_length,
    fsz,
    MAX_QUEUE,
    parse_minutes,
    get_all_files,
    compute_hashes,
    group_similar_files,
    EXCLUDE_DIRS,
    DICT_FILE,
    load_dictionary,
    setup_readline,
    translate,
    prefix_search,
    fuzzy_search,
    interactive_mode,
    OUTPUT_DIR,
    ARCHIVE_EXTENSIONS,
    get_unique_filepath,
    extract_entities_from_content,
    is_python_file_no_extension,
    process_single_file,
    process_archive,
    worker_process,
    get_current_folder_name,
    folder_exists_in_db,
    get_imports_from_file,
    copy_groups,
    write_report,
    colorize_score,
    write_matrix,
    main,
    safe_mkdir,
    cwd,
    process_file,
    collect_files_by_extension,
    main,
    OUTPUT_DIR,
    ALLOWED_PYTHON_EXTENSIONS,
    MAX_CHARS,
    clean_file,
    get_mode,
    SIZE_THRESHOLD,
    OLD_PRINT_RE,
    _open_source,
    _read_text,
    _has_rich_print_import,
    regex_flag,
    tokenizer_confirm,
    fsz,
    gsz,
    logger,
    count_lines_of_code,
    scan_directory,
    save_file,
    find_chunk_boundary,
    chunk_text,
    translate_file,
    is_english,
    find_site_packages,
    list_installed_packages,
    get_wheel_tags,
    copy_package_files,
    copy_dist_info,
    copy_scripts,
    build_wheel,
    repack,
    ERROR_DIR,
    OK_DIR,
    ensure_dirs,
    unique_destination,
    get_installed_debian_packages,
    save_packages,
    main,
    translate_chunk,
    translate_file,
    chunk_text,
    write_text_file,
    build_output_path,
    SUPPORTED_FORMATS,
    is_text_file,
    INPUT_FILE,
    OUTPUT_FILE,
    translate_word,
    main,
    EXCLUDE_PREFIXES,
    parser,
    EXCLUDE_DIRS,
    ALLOWED_EXT,
    CHUNK_SIZE,
    LOG_EXT,
    PATTERNS,
    ValidationError,
    PY_LANGUAGE,
    parser,
    should_preserve_comment,
    find_docstring_ranges,
    py_version,
    TIMESTAMP_RE,
    to_ms,
    from_ms,
    THRESHOLD,
    video,
    txtfile,
    OUT_DIR,
    extract_file,
    folder_imports,
    get_dir_size,
    extract_zst_file,
    find_archives,
    VALID,
    get_node_text,
    get_relative_path,
    processed_files_count,
    folders_found,
    total_definitions,
    BASE_DIR,
    N_JOBS,
    compress_chunk,
    _executor,
    get_dirs,
    main,
    OUT_PREFIX,
    CHUNK_SIZE,
    QUERY_STRING,
    should_preserve_comment,
    MAX_WORKERS,
    find_html_files,
    OUTPUT_DIR,
    ASSETS_DIR,
    TIMEOUT,
    MAX_WORKERS,
    get_all_dist_info_dirs,
    EXCLUDE_PREFIXES,
    get_sha256,
    find_png_files,
    ts_remover,
    EXCLUDED,
    read_requirements,
    safe_rename,
    unique_path,
    EXCLUDED_DIRS,
    format_time,
    ANSI_RESET,
    main,
    fsz,
    is_git_repo,
    gather_python_files,
    worker,
    find_dist_info_dir,
    UNPACKED_WHEELS_SOURCE_DIR,
    WHEELS_OUTPUT_DIR,
    find_dist_info_dir,
    env_vars,
    env_var_pattern,
    output_filename,
    OUTPUT_FILE,
    sha256_text,
    is_const_name,
    FONT_EXTENSIONS,
    FONT_SIZES,
    find_fonts,
    main,
    setup_logging,
    MAX_WORKERS,
    main,
    INPUT_FILE,
    main,
    can_fetch,
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
