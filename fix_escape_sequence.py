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

import difflib
import re
from pathlib import Path


def show_diff(text1, text2):
    diff = difflib.unified_diff(text1.splitlines(keepends=True), text2.splitlines(keepends=True), lineterm="")
    changed_lines = [line for line in diff if line.startswith(("+", "-"))]
    if changed_lines:
        print("--- Differences ---")
        for line in changed_lines:
            print(line, end="")
        print("-----------------")


def fix_escape_sequences(directory: Path):
    for path in directory.rglob("*.py"):
        if not path.is_symlink():
            try:
                content = path.read_text(encoding="utf-8")
                pattern = re.compile("^(\\s*\\w+\\s*=\\s*)([\"\\'])(?![rR])(.*?)\\2", re.MULTILINE)

                def replacer(match):
                    var_name_part = match.group(1)
                    quote_char = match.group(2)
                    string_content = match.group(3)
                    needs_raw_conversion = False
                    if re.search("\\\\(?![\"\\\\ntrvaf0x\\'])", string_content) or "\\\\" in string_content:
                        needs_raw_conversion = True
                    if re.search("\\\\(?![\\\\\\'\"ntr\\x00-\\x1f_])", string_content):
                        needs_raw_conversion = True
                    if "\\\\" in string_content:
                        needs_raw_conversion = True
                    if needs_raw_conversion:
                        return f"{var_name_part}r{quote_char}{string_content}{quote_char}"
                    return match.group(0)

                new_content = pattern.sub(replacer, content)
                if new_content != content:
                    show_diff(content, new_content)
                    backup_path = path.with_name(path.name + ".bak")
                    backup_path.write_text(content, encoding="utf-8")
                    path.write_text(new_content, encoding="utf-8")
                    print(f"Fixed {path.relative_to(directory)}")
            except Exception as e:
                print(f"Error processing {path}: {e}")


if __name__ == "__main__":
    cwd = Path.cwd()
    fix_escape_sequences(cwd)
