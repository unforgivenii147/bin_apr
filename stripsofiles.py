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

import time
from pathlib import Path

from dh import SoFileStripper


class BatchStripper:
    @staticmethod
    def strip_by_size_threshold(
        directory: str, min_size_mb: float = 1.0, verbose: bool = False, verify: bool = True
    ) -> dict:
        print(f"\nStripping .so files larger than {min_size_mb} MB...")
        so_files = list(Path(directory).rglob("*.so*"))
        min_bytes = min_size_mb * 1024 * 1024
        large_files = [f for f in so_files if f.stat().st_size >= min_bytes]
        stripper = SoFileStripper(verbose=verbose, verify_ctypes=verify)
        for so_file in large_files:
            stripper.process_file(so_file)
        return stripper.stats

    @staticmethod
    def strip_by_extension(
        directory: str, extensions: list[str] | None = None, verbose: bool = False, verify: bool = True
    ) -> dict:
        if extensions is None:
            extensions = [".so", ".so.1", ".so.6"]
        print(f"\nStripping .so files with extensions: {extensions}")
        so_files = []
        for ext in extensions:
            so_files.extend(Path(directory).rglob(f"*{ext}"))
        so_files = list(set(so_files))
        stripper = SoFileStripper(verbose=verbose, verify_ctypes=verify)
        for so_file in so_files:
            stripper.process_file(so_file)
        return stripper.stats

    @staticmethod
    def strip_exclude_patterns(
        directory: str, exclude_patterns: list[str] | None = None, verbose: bool = False, verify: bool = True
    ) -> dict:
        if exclude_patterns is None:
            exclude_patterns = ["test", "debug", "profile"]
        print(f"\nStripping .so files (excluding: {exclude_patterns})...")
        so_files = [
            f for f in Path(directory).rglob("*.so*") if not any((pattern in f.name for pattern in exclude_patterns))
        ]
        stripper = SoFileStripper(verbose=verbose, verify_ctypes=verify)
        for so_file in so_files:
            stripper.process_file(so_file)
        return stripper.stats

    @staticmethod
    def strip_with_retry(directory: str, max_retries: int = 3, verbose: bool = False, verify: bool = True) -> dict:
        print(f"\nStripping with retry logic (max {max_retries} attempts)...")
        so_files = list(Path(directory).rglob("*.so*"))
        stripper = SoFileStripper(verbose=verbose, verify_ctypes=verify)
        for so_file in so_files:
            for attempt in range(max_retries):
                result = stripper.process_file(so_file)
                if result["success"]:
                    break
                if attempt < max_retries - 1:
                    if verbose:
                        print(f"  Retry {attempt + 1}/{max_retries - 1}...")
                    time.sleep(1)
        return stripper.stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Batch .so file stripping with ctypes verification")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    size_parser = subparsers.add_parser("size", help="Strip by size threshold")
    size_parser.add_argument("directory", nargs="?", default=".")
    size_parser.add_argument("--min-mb", type=float, default=1.0, help="Minimum size in MB")
    size_parser.add_argument("-v", "--verbose", action="store_true")
    size_parser.add_argument("--no-verify", action="store_true", help="Skip ctypes verification")
    ext_parser = subparsers.add_parser("ext", help="Strip by extensions")
    ext_parser.add_argument("directory", nargs="?", default=".")
    ext_parser.add_argument("--extensions", nargs="+", default=[".so", ".so.1", ".so.6"])
    ext_parser.add_argument("-v", "--verbose", action="store_true")
    ext_parser.add_argument("--no-verify", action="store_true", help="Skip ctypes verification")
    excl_parser = subparsers.add_parser("exclude", help="Strip excluding patterns")
    excl_parser.add_argument("directory", nargs="?", default=".")
    excl_parser.add_argument("--patterns", nargs="+", default=["test", "debug", "profile"])
    excl_parser.add_argument("-v", "--verbose", action="store_true")
    excl_parser.add_argument("--no-verify", action="store_true", help="Skip ctypes verification")
    retry_parser = subparsers.add_parser("retry", help="Strip with retry")
    retry_parser.add_argument("directory", nargs="?", default=".")
    retry_parser.add_argument("--max-retries", type=int, default=3)
    retry_parser.add_argument("-v", "--verbose", action="store_true")
    retry_parser.add_argument("--no-verify", action="store_true", help="Skip ctypes verification")
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    verify = not args.no_verify
    if args.command == "size":
        BatchStripper.strip_by_size_threshold(args.directory, args.min_mb, args.verbose, verify)
    elif args.command == "ext":
        BatchStripper.strip_by_extension(args.directory, args.extensions, args.verbose, verify)
    elif args.command == "exclude":
        BatchStripper.strip_exclude_patterns(args.directory, args.patterns, args.verbose, verify)
    elif args.command == "retry":
        BatchStripper.strip_with_retry(args.directory, args.max_retries, args.verbose, verify)


if __name__ == "__main__":
    main()
