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

import multiprocessing as mp
import os
import sys
from pathlib import Path

import tree_sitter_python
from tree_sitter import Node, Parser

_parser = None


def init_worker():
    global _parser
    _parser = Parser()
    _parser.set_language(tree_sitter_python.language())


def is_preserved_comment(source_bytes: bytes, node: Node) -> bool:
    text = source_bytes[node.start_byte : node.end_byte]
    if node.start_byte == 0 and text.startswith(b"#!"):
        return True
    stripped = text.lstrip(b"#").strip()
    return bool(stripped.startswith((b"type:", b"fmt:")))


def collect_nodes_to_remove(source_bytes: bytes, node: Node) -> list[Node]:
    to_remove = []
    if node.type == "comment" and (not is_preserved_comment(source_bytes, node)):
        to_remove.append(node)
    if node.type == "string":
        parent = node.parent
        if parent and parent.type == "expression_statement":
            grandparent = parent.parent
            if grandparent and grandparent.type == "block":
                for i, child in enumerate(grandparent.children):
                    if child == parent:
                        if i == 0:
                            to_remove.append(node)
                        break
    for child in node.children:
        to_remove.extend(collect_nodes_to_remove(source_bytes, child))
    return to_remove


def process_file(filepath: str) -> tuple[str, bool]:
    global _parser
    try:
        source_bytes = Path(filepath).read_bytes()
        tree = _parser.parse(source_bytes)
        root = tree.root_node
        to_delete = collect_nodes_to_remove(source_bytes, root)
        if not to_delete:
            return (filepath, True)
        to_delete.sort(key=lambda n: n.start_byte, reverse=True)
        new_source = bytearray(source_bytes)
        for node in to_delete:
            del new_source[node.start_byte : node.end_byte]
        Path(filepath).write_bytes(new_source)
        return (filepath, True)
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return (filepath, False)


def main():
    py_files = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        py_files.extend((os.path.join(root, file) for file in files if file.endswith(".py")))
    if not py_files:
        print("No Python files found.")
        return
    print(f"Found {len(py_files)} Python files. Processing...")
    pool = mp.Pool(initializer=init_worker)
    results = pool.map(process_file, py_files)
    pool.close()
    pool.join()
    successes = [f for f, ok in results if ok]
    failures = [f for f, ok in results if not ok]
    print(f"Processed {len(successes)} files successfully.")
    if failures:
        print(f"Failed to process {len(failures)} files:")
        for f in failures:
            print(f"  {f}")


if __name__ == "__main__":
    try:
        import tree_sitter_python
    except ImportError:
        print("Error: Missing required package. Please install tree-sitter==0.25.2 and tree-sitter-python==0.25.0")
        sys.exit(1)
    main()
