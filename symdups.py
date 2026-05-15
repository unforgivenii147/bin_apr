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

import argparse
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import xxhash

BACKUP_FILE = ".symlink_backup.json"
MIN_FILE_SIZE = 8


def calculate_file_hash(filepath, chunk_size=8192):
    if not filepath.is_file():
        return None
    hasher = xxhash.xxh64()
    try:
        with Path(filepath).open("rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError as e:
        print(f"[ERROR] Reading {filepath}: {e}")
        return None


def find_duplicates(directory="."):
    print(f"[INFO] Scanning directory: {Path(directory).resolve()}")
    size_map = defaultdict(list)
    file_count = 0
    skipped_count = 0
    cwd = Path.cwd()
    for path in cwd.rglob("*"):
        if path.is_symlink() or path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        size = path.stat().st_size
        if size < MIN_FILE_SIZE:
            skipped_count += 1
            continue
        size_map[size].append(path)
        file_count += 1
    hash_map = defaultdict(list)
    potential_duplicates = [paths for paths in size_map.values() if len(paths) > 1]
    for paths in potential_duplicates:
        for path in paths:
            file_hash = calculate_file_hash(path)
            if file_hash:
                hash_map[file_hash].append(path)
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def choose_keeper(files):
    return min(files, key=lambda f: (len(str(f)), f))


def create_symlinks(duplicates, dry_run=False):
    backup_data = {"timestamp": datetime.now(tz=UTC).isoformat(), "operations": []}
    total_saved = 0
    symlink_count = 0
    for files in duplicates.values():
        keeper = choose_keeper(files)
        keeper_abs = Path(keeper).resolve()
        for duplicate in files:
            if duplicate == keeper:
                continue
            duplicate_abs = Path(duplicate).resolve()
            get_size = Path(duplicate).stat().st_size
            print(f"  Symlinking: {duplicate} -> {keeper_abs}")
            if not dry_run:
                backup_data["operations"].append(
                    {
                        "symlink": str(duplicate_abs),
                        "target": str(keeper_abs),
                        "original_existed": True,
                        "size": get_size,
                    }
                )
                try:
                    Path(duplicate).unlink()
                    Path(duplicate_abs).symlink_to(keeper_abs)
                    symlink_count += 1
                    total_saved += get_size
                except OSError as e:
                    print(f"  [ERROR] {e}")
            else:
                print(f"  [DRY RUN] Would replace {duplicate} with symlink to {keeper}")
                symlink_count += 1
                total_saved += get_size
    if not dry_run and symlink_count > 0:
        with Path(BACKUP_FILE).open("w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2)
        print(f"\n[INFO] Backup data saved to {BACKUP_FILE}")
    print(f"  Space saved: {total_saved / (1024 * 1024):.2f} MB")
    if dry_run:
        print("[DRY RUN] No changes were made")
    return symlink_count


def reverse_symlinks(backup_file=BACKUP_FILE):
    if not Path(backup_file).exists():
        print(f"[ERROR] Backup file {backup_file} not found!")
        return False
    with Path(backup_file).open(encoding="utf-8") as f:
        backup_data = json.load(f)
    restored_count = 0
    for op in backup_data["operations"]:
        symlink_path = op["symlink"]
        target_path = op["target"]
        if not Path(symlink_path).is_symlink():
            continue
        if not Path(target_path).exists():
            continue
        try:
            Path(symlink_path).unlink()
            import shutil

            shutil.copy2(target_path, symlink_path)
            restored_count += 1
        except OSError as e:
            print(f"[ERROR] Restoring {symlink_path}: {e}")
    backup_renamed = f"{backup_file}.restored.{datetime.now(tz=UTC).strftime('%Y%m%d_%H%M%S')}"
    Path(backup_file).rename(backup_renamed)
    print(f"[INFO] Backup file renamed to: {backup_renamed}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Find duplicate files and replace with symlinks (reversible)")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--reverse", action="store_true", help="Reverse previous symlinking operation")
    parser.add_argument("--backup-file", default=BACKUP_FILE, help=f"Backup file path (default: {BACKUP_FILE})")
    args = parser.parse_args()
    if args.reverse:
        reverse_symlinks(args.backup_file)
    else:
        duplicates = find_duplicates(args.directory)
        if not duplicates:
            print("\n[INFO] No duplicates found!")
            return
        print(f"\n[INFO] Found {len(duplicates)} groups of duplicates")
        print(f"[INFO] Total duplicate files: {sum((len(files) - 1 for files in duplicates.values()))}")
        if args.dry_run:
            print("\n[INFO] [DRY RUN MODE - No changes will be made]")
        create_symlinks(duplicates, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
