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
import os
import re
import sys
from pathlib import Path

from dh import is_binary


def process_file(file_path, search_text, replace_text=None, dry_run=False):
    try:
        content = Path(file_path).read_text(encoding="utf-8")
        replacement = replace_text if replace_text is not None else ""
        escaped_search = re.escape(search_text)
        pattern = re.compile(escaped_search)
        if pattern.search(content):
            if dry_run:
                matches = list(pattern.finditer(content))
                print(f"[DRY RUN] Found {len(matches)} match(es) in {file_path}")
                for i, match in enumerate(matches[:3]):
                    start = max(0, match.start() - 20)
                    end = min(len(content), match.end() + 20)
                    context = content[start:end]
                    context = context.replace("\n", " ").strip()
                    print(f"  Match {i + 1}: ...{context}...")
                if len(matches) > 3:
                    print(f"  ... and {len(matches) - 3} more matches")
            else:
                new_content = pattern.sub(replacement, content)
                Path(file_path).write_text(new_content, encoding="utf-8")
                print(f"Updated: {file_path}")
            return True
        return False
    except (UnicodeDecodeError, PermissionError, IsADirectoryError):
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False


def replace_in_files(search_text, replace_text=None, target_file=None, dry_run=False):
    exclude_dirs = {".git", "build", "dist", "__pycache__", "node_modules"}
    files_processed = 0
    files_changed = 0
    if target_file:
        if Path(target_file).is_file() and (not Path(target_file).is_symlink()):
            print(f"Processing file: {target_file}")
            if process_file(target_file, search_text, replace_text, dry_run):
                files_changed += 1
            files_processed += 1
        else:
            print(f"Error: {target_file} is not a valid file", file=sys.stderr)
        return (files_processed, files_changed)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in files:
            path = Path(root) / filename
            if path.is_symlink() or is_binary(path):
                continue
            files_processed += 1
            if process_file(path, search_text, replace_text, dry_run):
                files_changed += 1
            if files_processed % 100 == 0:
                print(f"Processed {files_processed} files...", end="\r")
    return (files_processed, files_changed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively replace or remove text in files.")
    parser.add_argument(
        "strings",
        nargs="+",
        help="Search text and optional replacement text. If only one string is provided, it will be removed.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument("-f", "--file", help="Process only the specified file instead of recursive directory search")
    args = parser.parse_args()
    if len(args.strings) == 2:
        search_text, replace_text = args.strings
        action = f"REPLACING '{search_text}' WITH '{replace_text}'"
    elif len(args.strings) == 1:
        search_text = args.strings[0]
        replace_text = None
        action = f"REMOVING '{search_text}'"
    else:
        parser.error("Please provide either one string (to remove) or two strings (search and replace)")
    if search_text.startswith(("'", '"')) and search_text.endswith(("'", '"')):
        search_text = search_text[1:-1]
    if args.dry_run:
        print("--- RUNNING IN DRY RUN MODE (No files will be modified) ---")
    print(f"--- {action} ---")
    files_processed, files_changed = replace_in_files(
        search_text, replace_text, target_file=args.file, dry_run=args.dry_run
    )
    print(f"\n--- Complete: Processed {files_processed} files, modified {files_changed} files ---")
