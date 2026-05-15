#!/data/data/com.termux/files/usr/bin/python3
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

import shutil
from pathlib import Path


def get_all_files(root: Path) -> list[Path]:
    return [p for p in root.glob("*") if p.is_file() and (not p.name.startswith(".")) and (p.name != "folderize.py")]


def safe_rename(src: Path, dest_dir: Path) -> Path:
    dest = dest_dir / src.name
    if not dest.exists():
        return dest
    stem, suffix = (dest.stem, dest.suffix)
    i = 1
    while True:
        new_name = f"{stem}_{i}{suffix}"
        dest = dest_dir / new_name
        if not dest.exists():
            return dest
        i += 1


def format_dir_name(start_idx: int, end_idx: int, total_files: int) -> str:
    return f"{start_idx}_{end_idx}"


def main():
    root = Path()
    files = get_all_files(root)
    if not files:
        logger.warning("No files found to process.")
        return
    total_files = len(files)
    print(f"Found {total_files:,} files")
    target_per_dir = max(1000, total_files // 10)
    n_dirs = max(2, (total_files + target_per_dir - 1) // target_per_dir)
    n_dirs = max(2, min(100, n_dirs))
    base_chunk = total_files // n_dirs
    remainder = total_files % n_dirs
    print(f"Creating {n_dirs} directories (~{base_chunk} files each)")
    created_dirs = []
    existing_dir_names = {p.name for p in root.iterdir() if p.is_dir()}
    for i in range(n_dirs):
        start = i * base_chunk + min(i, remainder)
        end = start + base_chunk + (1 if i < remainder else 0)
        dir_name = format_dir_name(start, end - 1, total_files)
        base_name = dir_name
        counter = 1
        while dir_name in existing_dir_names:
            dir_name = f"{base_name}_{counter}"
            counter += 1
        dir_path = root / dir_name
        dir_path.mkdir(exist_ok=True)
        created_dirs.append((dir_name, end - start))
        existing_dir_names.add(dir_name)
    print(f"Created dir '{dir_name}' for files [{start}, {end})")
    file_idx = 0
    for dir_name, count in created_dirs:
        dir_path = root / dir_name
        for _ in range(count):
            if file_idx >= total_files:
                break
            f = files[file_idx]
            dest = safe_rename(f, dir_path)
            shutil.move(str(f), str(dest))
            file_idx += 1
    print("=" * 50)
    print("✅ Folderization complete:")
    print(f"   Files processed: {total_files:,}")
    print(f"   Directories created: {len(created_dirs)}")
    print("=" * 50)
    print(f"\n{'Dir Name':<20} {'Files':>8}")
    print("-" * 30)
    for name, cnt in created_dirs:
        print(f"{name:<20} {cnt:>8}")
    print(f"\nTotal directories: {len(created_dirs)}")


if __name__ == "__main__":
    main()
