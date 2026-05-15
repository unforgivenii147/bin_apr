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
from pathlib import Path

import tree_sitter_python as tsp
from dh import get_pyfiles
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tsp.language())
parser = Parser(PY_LANGUAGE)


def extract_python_code_elements(filepath):
    try:
        with Path(filepath).open("rb") as f:
            tree = parser.parse(f.read())
    except Exception as e:
        print(f"Error parsing file {filepath}: {e}")
        return ([], [], [])
    functions = []
    classes = []
    constants = []
    imports = []
    nodes_to_visit = [tree.root_node]
    while nodes_to_visit:
        node = nodes_to_visit.pop(0)
        for child in node.children:
            if child.type == "function_definition":
                func_name_node = child.child_by_field_name("name")
                if func_name_node:
                    functions.append(func_name_node.text.decode("utf-8"))
            elif child.type == "class_definition":
                class_name_node = child.child_by_field_name("name")
                if class_name_node:
                    classes.append(class_name_node.text.decode("utf-8"))
            elif child.type == "assignment" and node.type not in {"import_statement", "import_from_statement"}:
                target = child.child_by_field_name("name")
                if target and target.text.decode("utf-8").isupper() and (len(target.text.decode("utf-8")) > 1):
                    if child.named_child_count == 2:
                        constants.append(target.text.decode("utf-8"))
            elif child.type == "import_statement":
                imports.extend(
                    (
                        import_node.text.decode("utf-8")
                        for import_node in child.children
                        if import_node.type == "dotted_name"
                    )
                )
            elif child.type == "import_from_statement":
                module_name_node = child.child_by_field_name("module_name")
                if module_name_node:
                    module_name = module_name_node.text.decode("utf-8")
                    for import_spec_node in child.children:
                        if import_spec_node.type == "import_spec":
                            for name_node in import_spec_node.children:
                                if name_node.type == "dotted_name":
                                    imports.append(f"{module_name}.{name_node.text.decode('utf-8')}")
                                elif name_node.type == "aliased_import":
                                    aliased_name_node = name_node.child_by_field_name("name")
                                    if aliased_name_node:
                                        imports.append(f"{module_name}.{aliased_name_node.text.decode('utf-8')}")
            if child.children:
                nodes_to_visit.append(child)
    return (functions, classes, constants, imports)


def process_directory(start_dir, output_dir):
    all_functions = {}
    all_classes = {}
    all_constants = {}
    all_imports = set()
    if not Path(output_dir).exists():
        Path(output_dir).mkdir(parents=True)
        print(f"Created output directory: {output_dir}")
    imports_output_path = os.path.join(output_dir, "imports.py")
    for path in get_pyfiles(start_dir):
        functions, classes, constants, imports = extract_python_code_elements(path)
        if functions:
            all_functions["relative_path"] = functions
        if classes:
            all_classes[relative_path] = classes
        if constants:
            all_constants[relative_path] = constants
        all_imports.update(imports)
    with Path(os.path.join(output_dir, "functions.txt")).open("w", encoding="utf-8") as f:
        for file, funcs in all_functions.items():
            f.write(f"# File: {file}\n")
            f.writelines((f"{func}\n" for func in funcs))
            f.write("\n")
    with Path(os.path.join(output_dir, "classes.txt")).open("w", encoding="utf-8") as f:
        for file, cls in all_classes.items():
            f.write(f"# File: {file}\n")
            f.writelines((f"{c}\n" for c in cls))
            f.write("\n")
    with Path(os.path.join(output_dir, "constants.txt")).open("w", encoding="utf-8") as f:
        for file, consts in all_constants.items():
            f.write(f"# File: {file}\n")
            f.writelines((f"{const}\n" for const in consts))
            f.write("\n")
    with Path(imports_output_path).open("w", encoding="utf-8") as f:
        if all_imports:
            f.write("# Extracted Imports\n\n")
            f.writelines((f"import {imp}\n" for imp in sorted(all_imports)))
        else:
            f.write("# No imports found.\n")
    print(f"\nExtraction complete. Results saved to '{output_dir}'.")
    print(f"Imports saved to '{imports_output_path}'.")


if __name__ == "__main__":
    current_directory = "."
    output_directory = "output"
    if not Path(output_directory).exists():
        Path(output_directory).mkdir(parents=True)
    print("Starting code element extraction...")
    process_directory(current_directory, output_directory)
