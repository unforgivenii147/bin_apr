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

import sys
from functools import partial
from pathlib import Path

from dh import mpf, unique_path


def rename_item_to_lowercase(path: Path, dry_run: bool = False, verbose: bool = False) -> tuple[Path, Path] | None:
    if not path.exists():
        if verbose:
            print(f"Warning: {path} does not exist. Skipping.", file=sys.stderr)
        return None
    new_name_lower = path.name.lower()
    if new_name_lower == path.name:
        if verbose:
            print(f"Skipping {path.name}: already lowercase.")
        return None
    new_path_candidate = path.parent / new_name_lower
    if new_path_candidate.exists() and new_path_candidate != path:
        new_path = unique_path(new_path_candidate)
        if verbose:
            print(f"Note: Target {new_path_candidate.name} already exists. Using unique path: {new_path.name}")
    else:
        new_path = new_path_candidate
    if dry_run:
        print(f"DRY RUN: Would rename '{path}' to '{new_path}'")
        return (path, new_path)
    try:
        Path(path).rename(new_path)
        if verbose:
            print(f"Renamed '{path.name}' to '{new_path.name}'")
        return (path, new_path)
    except OSError as e:
        print(f"Error renaming '{path.name}' to '{new_path.name}': {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred for '{path.name}': {e}", file=sys.stderr)
        return None


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    if dry_run:
        args.remove("--dry-run")
        print("--- DRY RUN MODE: No changes will be made ---")
    verbose = "--verbose" in args
    if verbose:
        args.remove("--verbose")
    if args:
        paths_to_process = [Path(p) for p in args]
    else:
        all_items = list(cwd.rglob("*"))
        paths_to_process = sorted(all_items, key=lambda p: len(p.parts), reverse=True)
    if not paths_to_process:
        print("No files or directories found to process.")
        return
    print(f"Found {len(paths_to_process)} items to potentially rename.")
    process_func_with_flags = partial(rename_item_to_lowercase, dry_run=dry_run, verbose=verbose)
    results = mpf(process_func_with_flags, paths_to_process)
    if dry_run:
        print("--- DRY RUN COMPLETE ---")
    else:
        renamed_count = sum((1 for r in results if r is not None))
        print(f"\nSummary: Renamed {renamed_count} items.")


if __name__ == "__main__":
    main()
