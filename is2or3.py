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
import sys
from pathlib import Path

from dh import get_files


def detect_version(file_path) -> None:
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    py2_score = 0
    py3_score = 0
    reasons = []
    try:
        tree = ast.parse(source)
        py3_score += 1
        reasons.append("Parsed successfully with Python 3 syntax.")
    except SyntaxError:
        print(f"{file_path.name}\nConfidence: High\nReason: Syntax error when parsed with Python 3.")
        return
    if "print " in source and "print(" not in source:
        py2_score += 2
        reasons.append("Uses print statement without parentheses (Python 2 style).")
    if "__future__" in source and "print_function" in source:
        py3_score += 2
        reasons.append("Uses 'from __future__ import print_function' (Python 3 compatibility).")
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.Await)):
            py3_score += 3
            reasons.append("Uses async/await syntax (Python 3 only).")
        if isinstance(node, ast.Try) and hasattr(node, "finalbody"):
            py3_score += 1
            reasons.append("Uses try/finally block (Python 3 syntax).")
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if hasattr(arg, "annotation") and arg.annotation is not None:
                    py3_score += 2
                    reasons.append("Uses function argument annotations (Python 3 feature).")
    if py2_score > py3_score:
        version = "2"
        confidence = "High" if py2_score - py3_score > 2 else "Medium"
    elif py3_score > py2_score:
        version = "3"
        confidence = "High" if py3_score - py2_score > 2 else "Medium"
    else:
        version = "3"
        confidence = "Low"
        reasons.append("No strong indicators found; defaulting to Python 3.")
    if version == "2":
        print(f"{file_path.name} : {version}\nConfidence: {confidence}\nReason(s):")


if __name__ == "__main__":
    args = sys.argv[1:]
    cwd = Path.cwd()
    files = [Path(f) for f in args] if args else get_files(cwd, extensions=[".py"])
    for file_path in files:
        detect_version(file_path)
