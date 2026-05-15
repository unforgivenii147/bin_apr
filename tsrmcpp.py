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

from pathlib import Path

import tree_sitter_cpp as tscpp
from dh import clean_blank_lines, run_command
from termcolor import cprint
from tree_sitter import Language, Parser


class TSCppRemover:
    def __init__(self) -> None:
        self.parser = Parser()
        self.language = Language(tscpp.language())
        self.parser.language = self.language

    def remove_comments(self, source: str) -> tuple[str, int]:
        source_bytes = source.encode("utf-8")
        tree = self.parser.parse(source_bytes)
        root = tree.root_node
        to_delete = []
        removed = 0
        for node in root.children:
            self._collect_comments(node, to_delete, source_bytes)
        new_source = source_bytes
        for start, end in sorted(to_delete, reverse=True):
            new_source = new_source[:start] + new_source[end:]
            removed += 1
        cleaned = new_source.decode("utf-8")
        cleaned = clean_blank_lines(cleaned)
        return (cleaned, removed)

    def _collect_comments(self, node, to_delete, source_bytes):
        if node.type == "comment":
            text = source_bytes[node.start_byte : node.end_byte].decode("utf-8").strip()
            if text.startswith("#"):
                return
            to_delete.append((node.start_byte, node.end_byte))
        for child in node.children:
            self._collect_comments(child, to_delete, source_bytes)


def validate_with_treesitter(parser, code: str) -> bool:
    tree = parser.parse(code.encode("utf-8"))
    return not tree.root_node.has_error


def validate_with_clang(file_path: Path) -> tuple[bool, str]:
    cmd = f"clang++ -std=c++20 -fsyntax-only {file_path!s}"
    ret, txt, err = run_command(cmd)
    if ret != 0:
        return (False, err)
    if ret == 0:
        return (True, txt)
    return None


def process_file(fp):
    file_path = Path(fp)
    before = file_path.stat().st_size
    remover = TSCppRemover()
    code = file_path.read_text(encoding="utf-8", errors="ignore")
    result, removed = remover.remove_comments(code)
    if removed == 0:
        cprint(f"[NO CHANGE] {file_path.name}", "blue")
        return
    if not validate_with_treesitter(remover.parser, result):
        cprint(f"[TS ERROR] {file_path.name} - changes discarded", "red")
        return
    file_path.write_text(result, encoding="utf-8")
    ok, _err = validate_with_clang(file_path)
    if not ok:
        cprint(f"[CLANG ERROR] {file_path.name} - reverting", "red")
        file_path.write_text(code, encoding="utf-8")
        return
    after = file_path.stat().st_size
    reduced = before - after
    cprint(f"[OK] {file_path.name} - removed {removed} comments, reduced {reduced} bytes", "cyan")


if __name__ == "__main__":
    exts = {".cpp", ".cc", ".cxx", ".hpp", ".h", ".hh", ".hxx", ".c"}
    for path in Path().rglob("*"):
        if path.is_file() and path.suffix in exts:
            process_file(path)
