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

from dh import fsz, get_files, gsz, mpf
from termcolor import cprint


def process_file(fp):
    try:
        content = fp.read_text(encoding="utf-8")
        tree = ast.parse(content)

        class OsPathTransformer(ast.NodeTransformer):
            def visit_Call(self, node):
                if (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and (node.func.value.id == "os")
                    and (node.func.attr == "path")
                ):
                    if isinstance(node.func.value, ast.Attribute) and node.func.attr == "join":
                        print(
                            f"Warning: os.path.join found in {file_path}. Requires manual review for Path division operator. Node: {ast.dump(node)}"
                        )
                        return node
                    if node.func.attr == "listdir":
                        print(
                            f"Info: os.listdir found in {file_path}. Consider using Path(path).iterdir(). Node: {ast.dump(node)}"
                        )
                        return node
                    if node.func.attr == "remove":
                        print(
                            f"Info: os.remove found in {file_path}. Replacing with Path.unlink(). Node: {ast.dump(node)}"
                        )
                        new_node = ast.Call(
                            func=ast.Attribute(value=ast.Name(id="Path"), attr="unlink", ctx=ast.Load()),
                            args=node.args,
                            keywords=node.keywords,
                        )
                        return ast.copy_location(new_node, node)
                    if node.func.attr == "splitext":
                        print(
                            f"Info: os.path.splitext found in {file_path}. Replacing with Path.stem/suffix. Node: {ast.dump(node)}"
                        )
                        return node
                elif (
                    isinstance(node.func, ast.Name)
                    and node.func.id == "os"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and ("remove" in node.args[0].value)
                ):
                    print(
                        f"Warning: Direct os.remove(string) call found in {file_path}. Consider using Path.unlink(). Node: {ast.dump(node)}"
                    )
                    return node
                return self.generic_visit(node)

            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name) and node.value.id == "os" and (node.attr == "remove"):
                    print(
                        f"Info: os.remove attribute found in {file_path}. Replacing with Path.unlink(). Node: {ast.dump(node)}"
                    )
                    new_node = ast.Attribute(value=ast.Name(id="Path"), attr="unlink", ctx=ast.Load())
                    return ast.copy_location(new_node, node)
                return self.generic_visit(node)

        transformer = OsPathTransformer()
        new_tree = transformer.visit(tree)
        has_pathlib_import = any(
            (
                isinstance(node, ast.Import)
                and any((alias.name == "pathlib" for alias in node.names))
                or (isinstance(node, ast.ImportFrom) and node.module == "pathlib")
                for node in ast.walk(new_tree)
            )
        )
        if not has_pathlib_import:
            import_pathlib = ast.Import(names=[ast.alias(name="Path")])
            ast.fix_missing_locations(import_pathlib)
            new_tree.body.insert(0, import_pathlib)
            print(f"Info: Added import Path from pathlib to {file_path}")
        ast.fix_missing_locations(new_tree)
        new_content = ast.unparse(new_tree)
        try:
            ast.parse(new_content)
            print(f"Successfully validated and refactored: {file_path}")
            return (new_content, True)
        except SyntaxError as e:
            print(f"Syntax error in refactored {file_path}: {e}")
            return (content, False)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return (None, False)


def main():
    root_dir = Path.cwd()
    before = gsz(root_dir)
    args = sys.argv[1:]
    files = []
    if args:
        for arg in args:
            p = Path(arg)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                files.extend(get_files(p, recursive=True))
    else:
        files = get_files(root_dir)
    results = mpf(process_file, files)
    for _result in results:
        pass
    diffsize = before - gsz(root_dir)
    cprint(f"space change : {fsz(diffsize)}", "cyan")


if __name__ == "__main__":
    sys.exit(main())
