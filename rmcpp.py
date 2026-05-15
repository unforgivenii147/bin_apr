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

import sys
from multiprocessing import get_context
from pathlib import Path

import tree_sitter_cpp as tscpp
from dh import clean_blank_lines, get_files
from tree_sitter import Language, Parser, Query, QueryCursor

ts_remover = None


class TSCppRemover:
    def __init__(self) -> None:
        self.language = Language(tscpp.language())
        self.parser = Parser(self.language)
        self.query = Query(self.language, "\n            (comment) @comment\n        ")

    def remove_comments(self, source: str):
        source_bytes = source.encode("utf-8")
        tree = self.parser.parse(source_bytes)
        cursor = QueryCursor(self.query)
        matches = cursor.matches(tree.root_node)
        deletions = []
        comment_count = 0
        for _pattern_idx, captures_dict in matches:
            for nodes in captures_dict.values():
                for node in nodes:
                    start = node.start_byte
                    end = node.end_byte
                    text = source_bytes[start:end].decode("utf-8")
                    stripped = text.strip()
                    if stripped.startswith(("//!", "///", "/**", "/*!", "///<", "//!<")):
                        continue
                    comment_count += 1
                    if end < len(source_bytes) and source_bytes[end : end + 1] == b"\n":
                        end += 1
                    deletions.append((start, end))
        deletions = sorted(set(deletions), reverse=True)
        new_source = bytearray(source_bytes)
        for start, end in deletions:
            del new_source[start:end]
        new_source = bytes(new_source)
        tree = self.parser.parse(new_source)
        if tree.root_node.has_error:
            print("Warning: Resulted code has syntax errors, returning original")
            return (source, 0)
        cleaned = new_source.decode("utf-8")
        cleaned = clean_blank_lines(cleaned)
        return (cleaned, comment_count)


def ts_remover_initializer():
    global ts_remover
    ts_remover = TSCppRemover()


def process_file(path):
    global ts_remover
    try:
        code = path.read_text(encoding="utf-8")
        result, comments = ts_remover.remove_comments(code)
    except Exception as e:
        print(f"[ERROR] {path.name} processing: {e}")
        return ("error", path, 0)
    if comments:
        path.write_text(result, encoding="utf-8")
        print(f"[OK] {path.name}: {comments} comments removed")
        return ("changed", path, comments)
    print(f"[NO CHANGE] {path.name}")
    return ("nochange", path, 0)


if __name__ == "__main__":
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = (
        [Path(p) for p in args]
        if args
        else get_files(cwd, extensions=[".js", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx", ".hh"])
    )
    before = gsz(cwd)
    with get_context("spawn").Pool(processes=8, initializer=ts_remover_initializer) as pool:
        results = pool.map(process_file, files)
    diffsize = before - gsz(cwd)
    changed = sum((1 for r in results if r[0] == "changed"))
    errors = [r for r in results if r[0] == "error"]
    nochg = sum((1 for r in results if r[0] == "nochange"))
    print(f"Files: {len(files)} | Changed: {changed} | Unchanged: {nochg} | Errors: {len(errors)}")
    if errors:
        print("\nErrors in:")
        for _, fn, *_ in errors:
            print(f"  - {fn}")
    print(f"Size reduced: {fsz(diffsize)}")
