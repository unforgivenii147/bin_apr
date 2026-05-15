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

import argparse
import re
import shutil
from pathlib import Path


PRINT_PATTERN = re.compile("^\\s*print\\s+(?!\\()(.+)$")
PRINT_BARE_PATTERN = re.compile("^\\s*print\\s*$")
EXCEPT_PATTERN = re.compile("^\\s*except\\s+(\\S+)\\s*,\\s*(\\S+)\\s*:")


def fix_py2_to_py3_all(line):
    original = line
    line = line.replace("xrange(", "range(")
    line = line.replace("raw_input(", "input(")
    m = EXCEPT_PATTERN.match(line.strip())
    if m:
        indent = line[: len(line) - len(line.lstrip())]
        exc_type, exc_var = (m.group(1), m.group(2))
        line = f"{indent}except {exc_type} as {exc_var}:\n"
    return (line, line != original)


def fix_print_statements(text):
    lines = text.splitlines(True)
    new_lines = []
    changed = False
    for line in lines:
        stripped = line.strip()
        if PRINT_BARE_PATTERN.match(stripped):
            indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}print()\n")
            changed = True
            continue
        m = PRINT_PATTERN.match(stripped)
        if m:
            expr = m.group(1)
            indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}print({expr})\n")
            changed = True
            continue
        new_lines.append(line)
    return ("".join(new_lines), changed)


def apply_all_fixes(text):
    lines = text.splitlines(True)
    new_lines = []
    changed = False
    for line in lines:
        new_line, c1 = fix_py2_to_py3_all(line)
        new_line2, c2 = fix_print_statements(new_line)
        changed = changed or c1 or c2
        new_lines.append(new_line2)
    return ("".join(new_lines), changed)


changed_files = []
error_files = []


def process_file(path: Path, force=False, apply_all=False) -> None:
    try:
        original = path.read_text(encoding="utf-8")
        if apply_all:
            fixed, changed = apply_all_fixes(original)
        else:
            fixed, changed = fix_print_statements(original)
        if changed:
            if not force:
                backup_path = path.with_suffix(path.suffix + ".bak")
                shutil.copy2(path, backup_path)
            path.write_text(fixed, encoding="utf-8")
            changed_files.append(str(path))
    except Exception as e:
        error_files.append((str(path), str(e)))


def scan_and_fix(root: Path, force, apply_all) -> None:
    for f in root.rglob("*.py"):
        process_file(f, force=force, apply_all=apply_all)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fix Python2 print statements and optionally apply all Py2→Py3 conversions."
    )
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite original files (no .bak backups)")
    parser.add_argument("-a", "--all", action="store_true", help="Apply all Python2→Python3 fixes")
    args = parser.parse_args()
    if not any(vars(args).values()):
        args.force = True
        args.all = True
    root = Path.cwd()
    scan_and_fix(root, force=args.force, apply_all=args.all)
    print("\n=== SUMMARY ===")
    print(f"Files changed: {len(changed_files)}")
    for f in changed_files:
        print("  -", f)
    print(f"\nFiles with errors: {len(error_files)}")
    for f, e in error_files:
        print(f"  - {f}: {e}")
