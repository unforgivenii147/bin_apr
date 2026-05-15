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

import argparse
import csv
import sys
from pathlib import Path


def find_site_packages():
    import site

    site_packages = site.getsitepackages()
    valid_paths = [p for p in site_packages if p is not None]
    if not valid_paths:
        user_site = site.getusersitepackages()
        if user_site and Path(user_site).exists():
            valid_paths = [user_site]
    return valid_paths


def update_record_file(record_path):
    try:
        with record_path.open(encoding="utf-8") as f:
            lines = list(csv.reader(f))
        original_count = len(lines)
        filtered_lines = []
        for row in lines:
            if not row:
                continue
            file_path = row[0] if row else ""
            if (
                file_path.endswith(".pyc")
                or file_path in {"direct_url.json", "INSTALLER"}
                or file_path.startswith("LICENSE")
            ):
                continue
            filtered_lines.append(row)
        if len(filtered_lines) == original_count:
            return False
        with record_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(filtered_lines)
        print(f"  Updated: {record_path} (removed {original_count - len(filtered_lines)} entries)")
        return True
    except Exception as e:
        print(f"  Error processing {record_path}: {e}", file=sys.stderr)
        return False


def scan_and_update(site_packages_dirs):
    total_updated = 0
    total_files = 0
    for site_dir in site_packages_dirs:
        if not Path(site_dir).exists():
            print(f"Directory does not exist: {site_dir}")
            continue
        print(f"\nScanning: {site_dir}")
        for path in Path(site_dir).rglob("*"):
            if path.name == "RECORD" and update_record_file(path):
                total_updated += 1
    return (total_files, total_updated)


def main():
    parser = argparse.ArgumentParser(
        description="Remove .pyc and direct_url.json references from RECORD files in site-packages"
    )
    parser.add_argument(
        "--site-dir",
        "-s",
        action="append",
        help="Specific site-packages directory to scan (can be used multiple times)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print more detailed information")
    args = parser.parse_args()
    site_dirs = args.site_dir or find_site_packages()
    if not site_dirs:
        print("Error: Could not find site-packages directory", file=sys.stderr)
        sys.exit(1)
    print(f"Python version: {sys.version}")
    print(f"Site packages directories: {', '.join(site_dirs)}")
    total_files, total_updated = scan_and_update(site_dirs)
    print(f"\n{'=' * 50}")
    print("Summary:")
    print(f"  Total RECORD files found: {total_files}")
    print(f"  Files that would be/are updated: {total_updated}")


if __name__ == "__main__":
    main()
