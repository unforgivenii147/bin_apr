#!/data/data/com.termux/files/usr/bin/python

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

import contextlib
import subprocess
from multiprocessing import cpu_count
from pathlib import Path


EXCLUDE_DIRS = {".git", "__pycache__"}


def should_skip(path: Path) -> bool:
    return any((part in EXCLUDE_DIRS for part in path.parts))


def minify_with_jq(path: Path):
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        size_before = path.stat().st_size
        result = subprocess.run(["jq", "-c", ".", str(path)], capture_output=True)
        if result.returncode != 0:
            return (str(path), False, 0, 0, result.stderr.decode().strip())
        minified_bytes = result.stdout.strip()
        size_after = len(minified_bytes)
        if size_before == size_after:
            return (str(path), False, size_before, size_after, None)
        Path(tmp_path).write_bytes(minified_bytes)
        Path(tmp_path).replace(path)
        return (str(path), True, size_before, size_after, None)
    except Exception as e:
        return (str(path), False, 0, 0, str(e))
    finally:
        if tmp_path.exists():
            with contextlib.suppress(Exception):
                tmp_path.unlink()


def collect_json_files(root: Path):
    for path in root.rglob("*.json"):
        if path.is_file() and (not should_skip(path)):
            yield path


def human_readable(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} PB"


def main():
    root = Path.cwd()
    files = list(collect_json_files(root))
    if not files:
        print("No JSON files found.")
        return
    workers = min(cpu_count(), len(files))
    print(f"Processing {len(files)} files using {workers} workers...\n")
    modified = 0
    errors = 0
    total_before = 0
    total_after = 0
    with Pool(processes=workers) as pool:
        for filepath, changed, before, after, err in pool.imap_unordered(minify_with_jq, files):
            if err:
                print(f"[ERROR] {filepath} -> {err}")
                errors += 1
                continue
            total_before += before
            total_after += after
            if changed:
                print(f"[OK] {filepath}")
                modified += 1
    reduced = total_before - total_after
    percent = reduced / total_before * 100 if total_before else 0
    print("\n--- Summary ---")
    print(f"Total files     : {len(files)}")
    print(f"Modified        : {modified}")
    print(f"Errors          : {errors}")
    print(f"Original size   : {human_readable(total_before)}")
    print(f"New size        : {human_readable(total_after)}")
    print(f"Total reduced   : {human_readable(reduced)} ({percent:.2f}%)")


if __name__ == "__main__":
    main()
