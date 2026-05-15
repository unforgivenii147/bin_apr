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

import os
import sqlite3
from pathlib import Path


def get_current_folder_name():
    return Path(Path.cwd()).name


def folder_exists_in_db(cursor, folder_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (folder_name,))
    return cursor.fetchone() is not None


def create_folder_table(cursor, folder_name):
    cursor.execute(
        f'\n        CREATE TABLE IF NOT EXISTS "{folder_name}" (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            filename TEXT NOT NULL,\n            file_contents TEXT\n        )\n    '
    )


def read_file_contents(filepath):
    try:
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        for encoding in encodings:
            try:
                with Path(filepath).open(encoding=encoding) as f:
                    return f.read(1024 * 1024)
            except (UnicodeDecodeError, UnicodeError):
                continue
        return "[Binary file content not stored]"
    except PermissionError:
        return "[Permission denied - cannot read file]"
    except Exception as e:
        return f"[Error reading file: {e!s}]"


def get_files_in_current_dir():
    current_dir = Path.cwd()
    files = []
    try:
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if Path(item_path).is_file():
                print(f"  Reading: {item}")
                contents = read_file_contents(item_path)
                files.append({"filename": item, "contents": contents})
    except PermissionError:
        print("Warning: Permission denied accessing some files")
    return files


def insert_files(cursor, folder_name, files):
    for file_info in files:
        cursor.execute(
            f'\n            INSERT INTO "{folder_name}" (filename,  file_contents)\n            VALUES (?, ?)\n        ',
            (file_info["filename"], file_info["contents"]),
        )


def main():
    db_path = "/sdcard/pkg.db"
    default_name = get_current_folder_name()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if folder_exists_in_db(cursor, folder_name):
        folder_name = default_name + "_new"
    create_folder_table(cursor, folder_name)
    files = get_files_in_current_dir()
    if not files:
        print("No files found in current directory!")
    else:
        insert_files(cursor, folder_name, files)
        conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
