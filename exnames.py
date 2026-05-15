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

import re
import sys
from pathlib import Path


def load_names(names_filepath):
    names = set()
    try:
        with Path(names_filepath).open("r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:
                    parts = name.split()
                    if len(parts) >= 2:
                        first_initial_pattern = re.escape(parts[0][0].upper())
                        last_initial_pattern = re.escape(parts[-1][0].upper())
                        pattern_str = f"{first_initial_pattern}[\\w\\s\\-']+\\s+{last_initial_pattern}[\\w\\s\\-']+"
                        names.add((name, re.compile(pattern_str, re.IGNORECASE)))
                    else:
                        names.add((name, re.compile(re.escape(name[0].upper()) + "[\\w\\s\\-']+", re.IGNORECASE)))
    except FileNotFoundError:
        print(f"Error: Names file not found at {names_filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading names file: {e}")
        sys.exit(1)
    return names


def find_names_in_files(names_db_path="names.txt"):
    names_to_find = load_names(names_db_path)
    if not names_to_find:
        return
    found_names = {}
    current_dir = Path.cwd()
    for filepath in current_dir.rglob("*"):
        if filepath.is_file() and filepath.suffix in {
            ".txt",
            ".md",
            ".log",
            ".py",
            ".html",
            ".css",
            ".js",
            ".json",
            ".xml",
            ".yml",
            ".yaml",
        }:
            try:
                with Path(filepath).open("r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for original_name, pattern in names_to_find:
                        for match in pattern.finditer(content):
                            matched_span = match.span()
                            matched_text = match.group(0)
                            match_parts = matched_text.strip().split()
                            if len(match_parts) >= 2 and (
                                match_parts[0][0].upper() == original_name.split()[0][0].upper()
                                and match_parts[-1][0].upper() == original_name.split()[-1][0].upper()
                            ):
                                if original_name not in found_names:
                                    found_names[original_name] = []
                                entry = {"file": str(filepath.relative_to(current_dir)), "match": matched_text}
                                if entry not in found_names[original_name]:
                                    found_names[original_name].append(entry)
            except Exception as e:
                print(f"Could not read file {filepath}: {e}")
    if not found_names:
        print("No target names found in the specified files.")
        return
    print(f"Found names (from {names_db_path}):")
    for name, occurrences in found_names.items():
        print(f"\n- {name}:")
        for occ in occurrences:
            print(f"  - File: {occ['file']}, Match: '{occ['match']}'")


if __name__ == "__main__":
    names_database_path = "/sdcard/data/male_names"
    if len(sys.argv) > 1:
        names_database_path = sys.argv[1]
    find_names_in_files(names_database_path)
