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

from collections import defaultdict
from pathlib import Path

import tree_sitter_python as tsp
from tree_sitter import Language, Parser

parser = Parser()
parser.language = Language(tsp.language())
OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)
VALID = {"function_definition", "class_definition"}


def get_node_text(src: bytes, node):
    return src[node.start_byte : node.end_byte].decode()


def get_node_name(node):
    for child in node.children:
        if child.type == "identifier":
            return child.text.decode() if hasattr(child, "text") else None
    return None


def extract_functions_and_classes(src: bytes, tree):
    root = tree.root_node
    definitions = []

    def traverse(node):
        if node.type in VALID:
            name = get_node_name(node)
            node_text = get_node_text(src, node)
            decorators = []
            prev_node = node.prev_sibling
            while prev_node and prev_node.type == "decorator":
                decorators.append(get_node_text(src, prev_node))
                prev_node = prev_node.prev_sibling
            if decorators:
                node_text = "\n".join(reversed(decorators)) + "\n" + node_text
            definitions.append(
                {
                    "type": node.type.replace("_definition", ""),
                    "name": name,
                    "text": node_text,
                    "line": node.start_point.row + 1,
                }
            )
        for child in node.children:
            traverse(child)

    traverse(root)
    return definitions


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    try:
        return file_path.relative_to(base_path)
    except ValueError:
        return file_path


folder_definitions = defaultdict(lambda: defaultdict(list))
processed_files_count = 0
folders_found = set()
total_definitions = 0
for py in Path().rglob("*.py"):
    if any((part.startswith(".") for part in py.parts)) or "site-packages" in py.parts:
        continue
    if OUT_DIR in py.parents:
        continue
    try:
        src = py.read_bytes()
        tree = parser.parse(src)
        definitions = extract_functions_and_classes(src, tree)
        if definitions:
            folder_path = py.parent
            relative_folder = get_relative_path(folder_path, Path())
            folders_found.add(str(relative_folder))
            folder_definitions[relative_folder][py.name] = {"definitions": definitions, "path": py}
            processed_files_count += 1
            total_definitions += len(definitions)
    except Exception as e:
        print(f"⚠️  Error processing {py}: {e}")
for folder, files_dict in folder_definitions.items():
    if not files_dict:
        continue
    out_file = OUT_DIR / folder / "definitions.py"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    content_parts = []
    content_parts.extend(("#" + "=" * 78, "# TABLE OF CONTENTS", "#" + "=" * 78, ""))
    for file_name, file_data in sorted(files_dict.items()):
        content_parts.append(f"# File: {file_name}")
        def_counts = {"function": 0, "class": 0}
        for d in file_data["definitions"]:
            def_counts[d["type"]] += 1
        if def_counts["function"] > 0:
            content_parts.append(f"#   Functions: {def_counts['function']}")
        if def_counts["class"] > 0:
            content_parts.append(f"#   Classes: {def_counts['class']}")
        content_parts.append("")
    content_parts.extend(("#" + "=" * 78, "# DEFINITIONS", "#" + "=" * 78, ""))
    for file_name, file_data in sorted(files_dict.items()):
        content_parts.extend(
            (f"\n# {'=' * 76}", f"# File: {file_name}", f"# Path: {file_data['path']}", f"# {'=' * 76}\n")
        )
        classes = [d for d in file_data["definitions"] if d["type"] == "class"]
        functions = [d for d in file_data["definitions"] if d["type"] == "function"]
        if classes:
            content_parts.extend(("#" + "-" * 40, "# CLASSES", "#" + "-" * 40, ""))
            for i, cls in enumerate(classes):
                if i > 0:
                    content_parts.append("\n" + "#" + "-" * 38 + "\n")
                content_parts.append(f"# Line: {cls['line']}")
                if cls["name"]:
                    content_parts.append(f"# Class: {cls['name']}")
                content_parts.append(cls["text"])
        if functions:
            if classes:
                content_parts.append("\n" + "#" + "-" * 40)
            else:
                content_parts.append("#" + "-" * 40)
            content_parts.extend(("# FUNCTIONS", "#" + "-" * 40, ""))
            for i, func in enumerate(functions):
                if i > 0:
                    content_parts.append("\n" + "#" + "-" * 38 + "\n")
                content_parts.append(f"# Line: {func['line']}")
                if func["name"]:
                    content_parts.append(f"# Function: {func['name']}")
                content_parts.append(func["text"])
        content_parts.append("\n" + "#" + "=" * 78 + "\n")
    content = "\n".join(content_parts)
    header = "#!/usr/bin/env python\n"
    out_file.write_text(header + content)
    total_defs_in_folder = sum((len(f["definitions"]) for f in files_dict.values()))
    print(f"✅ saved: {out_file}")
    print(f"   📊 {len(files_dict)} files, {total_defs_in_folder} definitions")
    print(f"   📁 {folder}")
print(
    f"\n✨ Done! Processed {processed_files_count} files with {total_definitions} total definitions in {len(folder_definitions)} folder(s)"
)
if folders_found:
    print("📁 Folders:")
    for folder in sorted(folders_found):
        def_count = sum((len(f["definitions"]) for f in folder_definitions[Path(folder)].values()))
        file_count = len(folder_definitions[Path(folder)])
        print(f"   • {folder}: {file_count} files, {def_count} definitions")
