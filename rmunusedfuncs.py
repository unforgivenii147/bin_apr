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

import argparse
import ast
import multiprocessing as mp
import shutil
import traceback
from pathlib import Path


def find_unused_functions(source):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ([], ["SyntaxError while parsing file"])
    defined = set()
    called = set()

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            defined.add(node.name)
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                called.add(node.func.id)
            self.generic_visit(node)

    Visitor().visit(tree)
    unused = defined - called
    return (list(unused), [])


def remove_functions_from_source(source, unused_functions):
    tree = ast.parse(source)
    new_body = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in unused_functions:
            continue
        new_body.append(node)
    tree.body = new_body
    return ast.unparse(tree)


def process_file(filepath, dry_run=False):
    errors = []
    filepath = Path(filepath)
    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return (filepath, [], [f"Error reading file: {e}"])
    unused, parse_errors = find_unused_functions(source)
    errors.extend(parse_errors)
    if not unused:
        return (filepath, [], errors)
    try:
        new_source = remove_functions_from_source(source, unused)
    except Exception:
        errors.append("Error rewriting file:\n" + traceback.format_exc())
        return (filepath, unused, errors)
    if not dry_run:
        backup_path = filepath.with_suffix(filepath.suffix + ".bak")
        shutil.copy2(filepath, backup_path)
        filepath.write_text(new_source, encoding="utf-8")
    return (filepath, unused, errors)


def gather_python_files(root: Path):
    return [p for p in root.rglob("*.py") if p.is_file()]


def worker(args):
    return process_file(*args)


def main():
    parser = argparse.ArgumentParser(description="Remove unused functions recursively.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without modifying files.")
    parser.add_argument("--workers", type=int, default=mp.cpu_count(), help="Number of processes")
    args = parser.parse_args()
    root = Path()
    py_files = gather_python_files(root)
    print(f"Scanning {len(py_files)} Python files...")
    with mp.Pool(args.workers) as pool:
        results = pool.map(worker, [(f, args.dry_run) for f in py_files])
    print("\n=== RESULTS ===")
    for filepath, unused, errors in results:
        if unused:
            if args.dry_run:
                print(f"[DRY-RUN] Would remove {unused} from {filepath}")
            else:
                print(f"Removed {unused} from {filepath} (backup created)")
        for err in errors:
            print(f"[ERROR] {filepath}: {err}")


if __name__ == "__main__":
    main()
