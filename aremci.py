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

import ast
import os
import re
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


COMMENT_AND_DOCSTRING_REGEX = re.compile(
    "(?:^(\\s*)#.*$)|(?:^(\\s*)(''').*?(\\3)|^(\\s*)(\\\"{3}).*?(\\5))|(?:\\b(def|class)\\s+\\w+[^():]*\\([^)]*\\)\\s*:\\s*)(\\s*)((''').*?(\\7)|(\\\"{3}).*?(\\9))",
    re.MULTILINE | re.DOTALL,
)
DOCSTRING_START_REGEX = re.compile("^\\s*('''|\\\"{3}).*?(\\1)\\s*", re.MULTILINE | re.DOTALL)
MAX_WORKERS = os.cpu_count() - 1 or 1


def strip_comments_and_docstrings(file_path_str):
    file_path = Path(file_path_str)
    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
    original_content = ""
    try:
        original_content = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False
    cleaned_content = DOCSTRING_START_REGEX.sub("\\1", original_content, count=3)

    def replace_comments(match):
        _indent1, comment1, quote1, _indent2, _quote2, fn_type, indent3, quote3, quote4 = match.groups()
        if comment1:
            return ""
        if quote1:
            return match.group(0)
        if quote3 or quote4:
            return f"{fn_type}{indent3}"
        return match.group(0)

    no_single_line_comments = re.sub("^\\s*#.*$", "", original_content, flags=re.MULTILINE)
    try:
        tree = ast.parse(no_single_line_comments)
        cleaned_content_heuristic = DOCSTRING_START_REGEX.sub("\\1", no_single_line_comments, count=3)
        try:
            ast.parse(cleaned_content_heuristic)
            final_code = cleaned_content_heuristic
        except SyntaxError:
            print(f"Syntax error after stripping comments/docstrings from {file_path}. Reverting.")
            return False
    except SyntaxError as e:
        print(f"Original code has syntax error: {file_path} - {e}. Skipping.")
        return False
    try:
        shutil.copy2(file_path, backup_path)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Error creating backup for {file_path}: {e}")
        return False
    try:
        Path(file_path).write_text(final_code, encoding="utf-8")
        print(f"Successfully stripped comments/docstrings from {file_path}")
        return True
    except Exception as e:
        print(f"Error writing cleaned file {file_path}: {e}")
        try:
            shutil.move(backup_path, file_path)
            print(f"Restored original content from backup for {file_path}")
        except Exception as restore_e:
            print(f"CRITICAL ERROR: Failed to write cleaned file and restore backup for {file_path}: {restore_e}")
        return False


def find_python_files_recursively(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)


def process_directory(directory):
    python_files = list(find_python_files_recursively(directory))
    print(f"Found {len(python_files)} Python files to process.")
    processed_count = 0
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(strip_comments_and_docstrings, file_path): file_path for file_path in python_files}
        for future in futures:
            file_path = futures[future]
            try:
                success = future.result()
                if success:
                    processed_count += 1
            except Exception as e:
                print(f"Error processing future for {file_path}: {e}")
    print(
        f"\nFinished processing. Successfully stripped comments/docstrings from {processed_count}/{len(python_files)} files."
    )


if __name__ == "__main__":
    target_directory = "."
    print(f"Starting comment and docstring stripping in directory: {Path(target_directory).resolve()}")
    process_directory(target_directory)
