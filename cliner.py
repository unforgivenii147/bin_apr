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

import mmap
import re
from pathlib import Path

from dh import mpf3

LOG_EXT = ".log"
MMAP_THRESHOLD = 1 * 1024 * 1024
NUM_WORKERS = 4
PATTERNS = [
    "\\^\\[",
    "\\[[\\dA-Z;]+m",
    "\\[\\d+[A-Z]",
    "\\[[\\dA-Z;]+",
    "\\^M",
    "\\(B",
    "\\(0",
    "\\x1b\\[[0-9;]*[A-Za-z]",
    "\\x1b\\([0-9AB]",
    "\\r",
    "\\x0f",
    "\\x0e",
]
COMPILED_PATTERNS = [re.compile(pattern) for pattern in PATTERNS]


def clean_line(line: str) -> str:
    cleaned = line
    for pattern in COMPILED_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    return re.sub(" {2,}", " ", cleaned)


def clean_file_small(path: Path) -> tuple:
    try:
        with path.open(encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        cleaned_lines = [clean_line(line) for line in lines]
        with path.open("w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
        return (path, True, "small file")
    except Exception as e:
        return (path, False, str(e))


def clean_file_large(path: Path) -> tuple:
    try:
        with path.open("r+b") as f:
            get_size = f.seek(0, 2)
            f.seek(0)
            if get_size == 0:
                return (path, True, "empty file")
            with mmap.mmap(f.fileno(), 0) as mmapped_file:
                content = mmapped_file.read().decode("utf-8", errors="ignore")
        lines = content.splitlines(keepends=True)
        cleaned_lines = [clean_line(line) for line in lines]
        cleaned_content = "".join(cleaned_lines)
        Path(path).write_text(cleaned_content, encoding="utf-8")
        return (path, True, "large file (mmap)")
    except Exception as e:
        return (path, False, str(e))


def clean_file_worker(path: Path) -> tuple:
    try:
        get_size = path.stat().st_size
        if get_size > MMAP_THRESHOLD:
            return clean_file_large(path)
        return clean_file_small(path)
    except Exception as e:
        return (path, False, str(e))


def main():
    cwd = Path.cwd()
    log_files = list(cwd.rglob(f"*{LOG_EXT}"))
    if not log_files:
        print(f"No {LOG_EXT} files found.")
        return
    print(f"Found {len(log_files)} log file(s).")
    results = mpf3(clean_file_worker, log_files)
    success_count = 0
    error_count = 0
    for path, success, message in results:
        if success:
            print(f"✓ Cleaned: {path} ({message})")
            success_count += 1
        else:
            print(f"✗ Error: {path} - {message}")
            error_count += 1
    print(f"\nDone. Successfully processed {success_count}/{len(log_files)} file(s).")
    if error_count > 0:
        print(f"Failed: {error_count} file(s).")


if __name__ == "__main__":
    main()
