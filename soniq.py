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

import mmap
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path

THRESHOLD = 1024 * 1024


def is_binary(path: Path, blocksize=4096):
    with path.open("rb") as f:
        sample = f.read(blocksize)
    if b"\x00" in sample:
        return True
    text_chars = bytes(range(32, 127)) + b"\n\r\t\x08"
    nontext = sum((c not in text_chars for c in sample))
    return nontext / max(len(sample), 1) > 0.3


def _process_chunk(chunk: list[str]):
    return [p.strip() for p in chunk if p.strip()]


def read_lines(path: Path):
    sz = path.stat().st_size
    if sz > THRESHOLD:
        with (
            path.open("r", encoding="utf-8", errors="ignore") as f,
            mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm,
        ):
            data = mm.read().decode("utf-8", "ignore")
            return data.splitlines()
    else:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def sort_uniq(path: Path, show_diff: bool = False):
    lines = read_lines(path)
    original_count = len(lines)
    if not original_count:
        return 0
    if original_count > 1000:
        num_workers = max(1, cpu_count() - 1)
        chunk_size = len(lines) // num_workers + 1
        chunks = [lines[i : i + chunk_size] for i in range(0, len(lines), chunk_size)]
        with Pool(num_workers) as pool:
            processed = pool.map(_process_chunk, chunks)
        all_lines = [line for group in processed for line in group]
    else:
        all_lines = [p.strip() for p in lines if p.strip()]
    unique_sorted = sorted(set(all_lines))
    diff_lines = set(all_lines) - set(unique_sorted)
    lines_removed = original_count - len(unique_sorted)
    path.write_text("\n".join(unique_sorted), encoding="utf-8")
    if show_diff and diff_lines:
        print("\nDuplicate lines removed:")
        for line in list(sorted(diff_lines))[:50]:
            print("  " + line)
        if len(diff_lines) > 50:
            print(f"... ({len(diff_lines) - 50} more not shown)")
    return lines_removed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sort_uniq_mp.py <filename> [--diff]")
        sys.exit(1)
    show_diff = True
    filename_arg = next((a for a in sys.argv[1:] if not a.startswith("--")), None)
    if not filename_arg:
        print("Error: missing filename argument.")
        sys.exit(1)
    path = Path(filename_arg)
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)
    if is_binary(path):
        print(f"{path.name} is binary. Skipped.")
        sys.exit(0)
    removed = sort_uniq(path, show_diff)
    if removed > 0:
        print(f"\nRemoved {removed} duplicate lines.")
    else:
        print("No change.")
