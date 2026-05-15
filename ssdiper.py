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

import json
import operator
from pathlib import Path

import ssdeep
from dh import get_files


def calculate_ssdeep_hash(filepath: Path, min_file_size: int = 1):
    try:
        if filepath.stat().st_size < min_file_size:
            return None
        with filepath.open("rb") as f:
            data = f.read()
            if len(data) < min_file_size:
                return None
            return ssdeep.hash(data)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except ssdeep.error as e:
        print(f"Error calculating ssdeep hash for {filepath}: {e}")
        return None
    except OSError as e:
        print(f"OS error accessing {filepath}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred for {filepath}: {e}")
        return None


def compare_files(file_paths: list[Path], similarity_threshold: int = 70):
    file_hashes = {}
    for filepath in file_paths:
        file_hash = calculate_ssdeep_hash(filepath)
        if file_hash:
            file_hashes[str(filepath)] = file_hash
    similarities = []
    cwd = Path.cwd()
    filepaths_list = list(file_hashes.keys())
    for i in range(len(filepaths_list)):
        for j in range(i + 1, len(filepaths_list)):
            filepath1_str = filepaths_list[i]
            filepath2_str = filepaths_list[j]
            hash1 = file_hashes[filepath1_str]
            hash2 = file_hashes[filepath2_str]
            try:
                score = ssdeep.compare(hash1, hash2)
                if score >= similarity_threshold:
                    similarities.append(
                        {
                            "file1": str(Path(filepath1_str).relative_to(cwd)),
                            "file2": str(Path(filepath2_str).relative_to(cwd)),
                            "similarity_score": score,
                        }
                    )
            except ssdeep.error as e:
                print(f"Error comparing hashes for {filepath1_str} and {filepath2_str}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred during comparison for {filepath1_str} and {filepath2_str}: {e}")
    similarities.sort(key=operator.itemgetter("similarity_score"), reverse=True)
    return similarities


def save_to_json(data, filename="simz.json"):
    try:
        with Path(filename).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data to JSON file '{filename}': {e}")


if __name__ == "__main__":
    cwd = Path.cwd()
    MIN_SIMILARITY_THRESHOLD = 30
    OUTPUT_JSON_FILE = "simz.json"
    files = get_files(cwd)
    if not files:
        print("No files found matching the criteria in the specified directory.")
    else:
        similar_file_pairs = compare_files(files, MIN_SIMILARITY_THRESHOLD)
        if similar_file_pairs:
            save_to_json(similar_file_pairs, OUTPUT_JSON_FILE)
        else:
            print(f"\nNo files found with similarity >= {MIN_SIMILARITY_THRESHOLD}%.")
