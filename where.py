from utils import (
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

import argparse
import shutil
import sys
import time
import traceback
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def parse_csv_exts(s: str | None) -> set[str] | None:
    if not s:
        return None
    parts = [p.strip().lower() for p in s.split(",") if p.strip()]
    if not parts:
        return None
    norm = set()
    for p in parts:
        if not p.startswith("."):
            p = "." + p
        norm.add(p)
    return norm


def file_matches_extensions(file_path: Path, allowed_exts: set[str] | None) -> bool:
    if allowed_exts is None:
        return True
    return file_path.suffix.lower() in allowed_exts


def file_matches_exclude(file_path: Path, excluded_exts: set[str] | None) -> bool:
    if excluded_exts is None:
        return False
    return file_path.suffix.lower() in excluded_exts


def human_size(nbytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(nbytes)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            if u == "B":
                return f"{int(size)} {u}"
            return f"{size:.2f} {u}"
        size /= 1024.0
    return f"{nbytes} B"


def safe_copy_file(src: Path, dst_root: Path, rel_path: Path, errors: list[str]) -> None:
    try:
        dst_path = dst_root / rel_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst_path)
    except Exception as e:
        msg = f"[copy-error] {src} -> {dst_root / rel_path}\n{e}\n{traceback.format_exc()}"
        errors.append(msg)


class ChangeHandler(FileSystemEventHandler):
    def __init__(
        self,
        root_dir: Path,
        copy_enabled: bool,
        dest_dir: Path,
        allowed_exts: set[str] | None,
        excluded_exts: set[str] | None,
        interval_sec: float,
        print_lock=None,
    ):
        super().__init__()
        self.root_dir = root_dir
        self.copy_enabled = copy_enabled
        self.dest_dir = dest_dir
        self.allowed_exts = allowed_exts
        self.excluded_exts = excluded_exts
        self.interval_sec = interval_sec
        self._errors: list[str] = []
        self._pending: dict[Path, str] = {}
        self._last_flush = time.time()

    def _rel(self, p: Path) -> Path:
        try:
            return p.relative_to(self.root_dir)
        except ValueError:
            return Path(p.name)

    def _queue(self, src_path: Path, reason: str) -> None:
        if src_path.exists() and (not src_path.is_file()):
            return
        if self.allowed_exts is not None and (not file_matches_extensions(src_path, self.allowed_exts)):
            return
        if self.excluded_exts is not None and file_matches_exclude(src_path, self.excluded_exts):
            return
        self._pending[src_path] = reason
        self._maybe_flush()

    def _maybe_flush(self) -> None:
        now = time.time()
        if now - self._last_flush >= self.interval_sec:
            self.flush()

    def flush(self) -> None:
        if not self._pending:
            self._last_flush = time.time()
            return
        for src_path, reason in list(self._pending.items()):
            rel_path = self._rel(src_path)
            if src_path.exists() and src_path.is_file():
                try:
                    sz = src_path.stat().st_size
                    size_str = human_size(sz)
                except Exception:
                    size_str = "unknown-size"
            else:
                size_str = "deleted"
            print(f"-  /{rel_path.as_posix()} | {reason} | {size_str}")
            if self.copy_enabled and src_path.exists() and src_path.is_file():
                safe_copy_file(src=src_path, dst_root=self.dest_dir, rel_path=rel_path, errors=self._errors)
        self._pending.clear()
        self._last_flush = time.time()
        if self._errors:
            print("\n[errors] copy operation errors:")
            for msg in self._errors:
                print(msg)
            print("-" * 80)
            self._errors.clear()

    def on_created(self, event):
        if event.is_directory:
            return
        self._queue(Path(event.src_path), "create")

    def on_modified(self, event):
        if event.is_directory:
            return
        self._queue(Path(event.src_path), "change")

    def on_deleted(self, event):
        if event.is_directory:
            return
        src_path = Path(event.src_path)
        if self.allowed_exts is not None and (not file_matches_extensions(src_path, self.allowed_exts)):
            return
        if self.excluded_exts is not None and file_matches_exclude(src_path, self.excluded_exts):
            return
        self._queue(src_path, "delete")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Watch a folder, print changes, and optionally copy changed/created files.")
    p.add_argument(
        "folder", nargs="?", default=str(Path.cwd()), help="Folder to watch (default: current working directory)."
    )
    p.add_argument("-c", "--copy", action="store_true", help="Copy changed/created files to destination.")
    p.add_argument(
        "-d",
        "--dest",
        default=str(Path.home() / "tmp" / "tgz"),
        help="Destination folder for copies (default: ~/tmp/tgz).",
    )
    p.add_argument(
        "-e",
        "--extensions",
        default=None,
        help="Comma-separated allowlist of file extensions to copy, e.g. 'svg,png,txt'. If omitted, copy all changed/created file types.",
    )
    p.add_argument(
        "-x",
        "--exclude",
        default=None,
        help="Comma-separated list of file extensions to exclude from copying, e.g. 'log,tmp'.",
    )
    p.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Watch interval (seconds) for batching/printing and copying (default: 1.0).",
    )
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    root_dir = Path(args.folder).expanduser().resolve()
    dest_dir = Path(args.dest).expanduser().resolve()
    if not root_dir.is_dir():
        print(f"Error: folder does not exist or is not a directory: {root_dir}")
        sys.exit(2)
    allowed_exts = parse_csv_exts(args.extensions)
    excluded_exts = parse_csv_exts(args.exclude)
    interval_sec = max(0.1, float(args.interval))
    if args.copy:
        dest_dir.mkdir(parents=True, exist_ok=True)
    handler = ChangeHandler(
        root_dir=root_dir,
        copy_enabled=bool(args.copy),
        dest_dir=dest_dir,
        allowed_exts=allowed_exts,
        excluded_exts=excluded_exts,
        interval_sec=interval_sec,
    )
    observer = Observer()
    observer.schedule(handler, str(root_dir), recursive=True)
    observer.start()
    print(f"Watching: {root_dir}")
    if args.copy:
        print(f"Copy enabled: destination = {dest_dir}")
    else:
        print("Copy disabled (printing only).")
    if allowed_exts is not None:
        print(f"Allowed extensions: {sorted(allowed_exts)}")
    if excluded_exts is not None:
        print(f"Excluded extensions: {sorted(excluded_exts)}")
    print(f"Interval: {interval_sec} sec (batch flush)\n")
    try:
        while True:
            time.sleep(interval_sec)
            handler.flush()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        try:
            handler.flush()
        except Exception:
            pass
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
