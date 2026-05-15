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

import re
import sys
from pathlib import Path


def parse_tree_file(tree_path):
    with Path(tree_path).open("r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines if line.strip()]
    root_line = lines[0].strip() if lines else ""
    root_name = re.sub("[├└│─]+", "", root_line).strip().rstrip("/")
    root_parts = [root_name] if root_name else []
    entries = []
    stack = [(0, root_parts)]
    for line in lines[1:]:
        if not line.strip():
            continue
        match = re.match("^([├└│ ]*)([├└]──\\s*)?(\\S.*)$", line)
        if not match:
            continue
        prefix, _marker, name = match.groups()
        name = name.strip()
        if name.startswith("#") or name == "":
            continue
        indent = len(prefix) // 4
        while stack and stack[-1][0] >= indent:
            stack.pop()
        current_path = stack[-1][1] if stack else []
        is_dir = name.endswith("/") or "." not in Path(name).name or any((c in name for c in ["/", "\\"]))
        name = name.rstrip("/")
        full_path = [*current_path, name]
        entries.append((indent, full_path, is_dir))
        if is_dir:
            stack.append((indent, full_path))
    return entries


def create_tree_from_entries(entries):
    created_dirs = set()
    for _indent, path_parts, is_dir in entries:
        if len(path_parts) == 1 and path_parts[0] == "dictionary-webapp":
            continue
        path = Path(*path_parts)
        if is_dir:
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.add(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()


def main():
    tree_file = sys.argv[1]
    if not Path(tree_file).exists():
        print(f"❌ Error: '{tree_file}' not found in current directory.")
        return
    print(f"📖 Parsing '{tree_file}'...")
    entries = parse_tree_file(tree_file)
    if not entries:
        print("⚠️  No valid entries found in tree file.")
        return
    print(f"✅ Parsed {len(entries)} entries.")
    print("📁 Creating folder structure...")
    create_tree_from_entries(entries)
    print("✨ Done! Folder structure created successfully.")


if __name__ == "__main__":
    main()
