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

import argparse
import sys
from pathlib import Path


EXCLUDED_NAMES: set[str] = {"tmp", "cache", "bin", ".git", "etc", "config", "var"}
EXCLUDED_PATH_COMPONENTS: set[str] = {".git", "tmp", "etc", "var", "config"}


def is_excluded(path: Path, root_path: Path) -> bool:
    if path.name in EXCLUDED_NAMES:
        return True
    try:
        relative_parts = path.relative_to(root_path).parts
        if any((part in EXCLUDED_PATH_COMPONENTS for part in relative_parts)):
            return True
    except ValueError:
        pass
    return bool(path.name.startswith("mc") and path.parent.name == "tmp")


def delete_empty_dirs_iterative(root: Path, dry_run: bool = False, verbose: bool = False) -> tuple[int, list[Path]]:
    removed_count: int = 0
    removed_dirs_list: list[Path] = []
    dirs_to_visit: list[Path] = [d for d in root.rglob("*") if d.is_dir()]
    dirs_to_visit.sort(key=lambda p: len(p.parts), reverse=True)
    if root.is_dir():
        dirs_to_visit.append(root)
    for path in dirs_to_visit:
        if not path.is_dir():
            continue
        if is_excluded(path, root):
            if verbose:
                print(f"Skipping excluded directory: {path.relative_to(root)}")
            continue
        try:
            if not any((entry for entry in path.iterdir() if entry.is_dir() or entry.is_file())):
                if verbose:
                    print(f"Empty directory found: {path.relative_to(root)}")
                if not dry_run:
                    path.rmdir()
                    removed_count += 1
                    removed_dirs_list.append(path)
                    if verbose:
                        print(f"  --> Removed: {path.relative_to(root)}")
                else:
                    print(f"  (Dry Run) Would remove: {path.relative_to(root)}")
        except PermissionError:
            print(f"[ERROR] Permission denied for: {path.relative_to(root)}", file=sys.stderr)
        except OSError as e:
            print(f"[ERROR] Could not process {path.relative_to(root)}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred with {path.relative_to(root)}: {e}", file=sys.stderr)
    return (removed_count, removed_dirs_list)


def main():
    parser = argparse.ArgumentParser(description="Find and remove empty directories, excluding specified ones.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="The root directory to start scanning from (default: current working directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run: show what would be deleted without actually deleting.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output, showing skipped and found directories."
    )
    args = parser.parse_args()
    root_path = args.path.resolve()
    if not root_path.is_dir():
        print(f"Error: The provided path '{root_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        print("--- DRY RUN MODE (no changes will be made) ---")
    removed_count, removed_dirs_list = delete_empty_dirs_iterative(
        root_path, dry_run=args.dry_run, verbose=args.verbose
    )
    if removed_count > 0:
        if args.dry_run:
            print(f"Would have removed {removed_count} empty directories:")
        else:
            print(f"removed {removed_count}")
        for d_path in sorted(removed_dirs_list):
            print(f"- {d_path.relative_to(root_path)}")
    else:
        print("No empty dir.")


if __name__ == "__main__":
    main()
