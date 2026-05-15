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


def get_size_str(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def folderize_by_extension(cwd):
    root_path = Path(cwd)
    extension_stats = {}
    for file_path in root_path.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()[1:] if file_path.suffix else "no_extension"
            size = file_path.stat().st_size
            if ext not in extension_stats:
                extension_stats[ext] = {"count": 0, "total_size": 0, "files": []}
            extension_stats[ext]["count"] += 1
            extension_stats[ext]["total_size"] += size
            extension_stats[ext]["files"].append(file_path)
    created_dirs = set()
    for ext, stats in extension_stats.items():
        target_dir = root_path / ext
        target_dir.mkdir(exist_ok=True)
        created_dirs.add(ext)
        for file_path in stats["files"]:
            if file_path.parent == target_dir:
                continue
            target_path = target_dir / file_path.name
            counter = 1
            while target_path.exists():
                target_path = target_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1
            shutil.move(str(file_path), str(target_path))
    for dir_path in sorted(root_path.glob("**/*"), key=lambda p: len(p.parts), reverse=True):
        if dir_path.is_dir() and dir_path != root_path:
            try:
                dir_path.rmdir()
                print(f"Removed empty directory: {dir_path.relative_to(root_path)}")
            except OSError:
                pass
    print("\n" + "=" * 50)
    print("ORGANIZATION SUMMARY")
    print("=" * 50)
    total_files = 0
    total_size = 0
    for ext in sorted(extension_stats.keys()):
        stats = extension_stats[ext]
        total_files += stats["count"]
        total_size += stats["total_size"]
        ext_display = ext or "no_extension"
        size_str = get_size_str(stats["total_size"])
        print(f"{ext_display:<15} : {stats['count']:4} file{('s' if stats['count'] != 1 else ' ')}  {size_str:>8}")
    print("-" * 50)
    print(f"{'TOTAL':<15} : {total_files:4} files  {get_size_str(total_size):>8}")
    print("=" * 50)
    return (created_dirs, extension_stats)


if __name__ == "__main__":
    target_dir = Path.cwd()
    print(f"Organizing files in: {target_dir}")
    created_dirs, stats = folderize_by_extension(target_dir)
    print(f"\nCreated {len(created_dirs)} extension folders.")
    print("Done!")
