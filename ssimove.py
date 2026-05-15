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

import ssdeep

SEARCH_DIR = Path.cwd()
OUTPUT_DIR = SEARCH_DIR / "output"
SIMILARITY_THRESHOLD = 60
MIN_GROUP_SIZE = 2


def calculate_fuzzy_hash(filepath: Path) -> str:
    try:
        return ssdeep.hash_from_file(str(filepath))
    except ssdeep.Error as e:
        print(f"Error calculating ssdeep hash for {filepath}: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected error for {filepath}: {e}")
        return ""


def find_similar_files(search_dir: Path, output_dir: Path, similarity_threshold: int, min_group_size: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_hashes: dict[Path, str] = {}
    for filepath in search_dir.rglob("*"):
        if filepath.is_file() and (not filepath.is_symlink()):
            hash_value = calculate_fuzzy_hash(filepath)
            if hash_value:
                file_hashes[filepath] = hash_value
    if not file_hashes:
        print("No files found or no hashes could be generated.")
        return
    similar_groups: dict[Path, list[Path]] = {}
    processed_files = set()
    file_paths = list(file_hashes.keys())
    num_files = len(file_paths)
    for i in range(num_files):
        current_file = file_paths[i]
        if current_file in processed_files:
            continue
        current_hash = file_hashes[current_file]
        current_group = [current_file]
        for j in range(i + 1, num_files):
            other_file = file_paths[j]
            if other_file in processed_files:
                continue
            other_hash = file_hashes[other_file]
            try:
                similarity = ssdeep.compare(current_hash, other_hash)
                if similarity >= similarity_threshold:
                    print(f"  - Found similarity ({similarity}/{current_hash} vs {other_hash} -> {other_file})")
                    current_group.append(other_file)
            except ssdeep.Error as e:
                print(f"Error comparing hashes for {current_file} and {other_file}: {e}")
            except Exception as e:
                print(f"Unexpected error comparing hashes for {current_file} and {other_file}: {e}")
        if len(current_group) >= min_group_size:
            processed_files.update(current_group)
            representative_file = current_group[0]
            similar_groups[representative_file] = current_group
            print(f"  -> Added group (starting with {representative_file.name}) with {len(current_group)} files.")
    print("\n--- Moving Similar Files ---")
    moved_files_count = 0
    group_counter = 0
    files_to_move = set()
    final_groups_to_move = []
    for rep_file, group in similar_groups.items():
        valid_group = [f for f in group if f not in processed_files or f == rep_file]
        if len(valid_group) >= min_group_size:
            final_groups_to_move.append(valid_group)
            files_to_move.update(valid_group)
    processed_files.update(files_to_move)
    for group in final_groups_to_move:
        group_counter += 1
        group_output_subdir = output_dir / f"group_{group_counter:03d}"
        group_output_subdir.mkdir(parents=True, exist_ok=True)
        print(f"Creating group directory: {group_output_subdir}")
        for file_to_move in group:
            try:
                dest_path = group_output_subdir / file_to_move.name
                if dest_path.exists():
                    print(f"  - Warning: Destination file already exists, skipping: {dest_path}")
                    continue
                shutil.move(str(file_to_move), str(dest_path))
                print(f"  - Moved: {file_to_move.name} to {group_output_subdir.name}/")
                moved_files_count += 1
            except FileNotFoundError:
                print(
                    f"  - Error: File not found during move (might have been moved already or deleted): {file_to_move}"
                )
            except Exception as e:
                print(f"  - Error moving {file_to_move.name}: {e}")
    print("\n--- Summary ---")
    if group_counter == 0:
        print("No groups of similar files found that met the criteria.")
    else:
        print(f"Moved {moved_files_count} files into {group_counter} groups.")
        print(f"Similar files have been moved to: {output_dir}")


if __name__ == "__main__":
    if Path.cwd() == SEARCH_DIR:
        print("INFO: Processing files in the current directory.")
    else:
        print(f"INFO: Processing files in: {SEARCH_DIR}")
    if SEARCH_DIR.resolve() == OUTPUT_DIR.resolve():
        print("ERROR: SEARCH_DIR and OUTPUT_DIR cannot be the same. Please configure them differently.")
    else:
        find_similar_files(
            search_dir=SEARCH_DIR,
            output_dir=OUTPUT_DIR,
            similarity_threshold=SIMILARITY_THRESHOLD,
            min_group_size=MIN_GROUP_SIZE,
        )
