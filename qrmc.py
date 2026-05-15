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
import multiprocessing
import operator
import os
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)
QUERY_STRING = "\n(comment) @comment\n(block\n  . (expression_statement\n    (string)) @docstring)\n(module\n  . (expression_statement\n    (string)) @docstring)\n"
query = Query(PY_LANGUAGE, QUERY_STRING)
cursor = QueryCursor(query)


def should_preserve_comment(content):
    content = content.strip()
    return any((content.startswith(p) for p in ["#!", "# type:", "# fmt:"]))


def strip_file(file_path):
    try:
        source_code = Path(file_path).read_text(encoding="utf-8")
        source_bytes = bytes(source_code, "utf8")
        tree = parser.parse(source_bytes)
        captures = cursor.captures(tree.root_node)
        modifications = []
        for node, tag in captures:
            if tag == "comment":
                comment_text = source_code[node.start_byte : node.end_byte]
                if not should_preserve_comment(comment_text):
                    modifications.append((node.start_byte, node.end_byte, ""))
            elif tag == "docstring":
                parent = node.parent
                if parent and parent.named_child_count == 1:
                    modifications.append((node.start_byte, node.end_byte, "pass"))
                else:
                    modifications.append((node.start_byte, node.end_byte, ""))
        if not modifications:
            return
        modifications.sort(key=operator.itemgetter(0), reverse=True)
        working_code = source_code
        for start, end, replacement in modifications:
            working_code = working_code[:start] + replacement + working_code[end:]
        try:
            ast.parse(working_code)
            Path(file_path).write_text(working_code, encoding="utf-8")
        except SyntaxError:
            pass
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def main():
    files = [os.path.join(r, f) for r, _, fs in os.walk(".") for f in fs if f.endswith(".py")]
    if not files:
        return
    print(f"Processing {len(files)} files using QueryCursor...")
    with multiprocessing.get_context("spawn").Pool(8) as pool:
        pool.map(strip_file, files)
    print("In-place cleanup complete.")


if __name__ == "__main__":
    main()
