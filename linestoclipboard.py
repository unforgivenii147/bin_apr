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

import subprocess
import sys
from pathlib import Path


def copy_lines_to_clipboard(filename: str, start_line: int, end_line: int | None = None):
    input_file = Path(filename)
    if not input_file.is_file():
        print(f"Error: File not found at '{filename}'", file=sys.stderr)
        sys.exit(1)
    try:
        with input_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"Error reading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}", file=sys.stderr)
        sys.exit(1)
    total_lines = len(lines)
    start_index = start_line - 1
    end_index = total_lines if end_line is None else end_line
    if not 0 <= start_index < total_lines:
        print(f"Error: Start line ({start_line}) is out of bounds. File has {total_lines} lines.", file=sys.stderr)
        sys.exit(1)
    if not 0 <= end_index <= total_lines:
        print(
            f"Error: End line ({(end_line if end_line is not None else 'end of file')}) is out of bounds. File has {total_lines} lines.",
            file=sys.stderr,
        )
        sys.exit(1)
    if start_index >= end_index:
        print(
            f"Error: Start line ({start_line}) must be before or equal to end line ({(end_line if end_line is not None else total_lines)}).",
            file=sys.stderr,
        )
        sys.exit(1)
    selected_lines = lines[start_index:end_index]
    content_to_copy = "".join(selected_lines)
    if not content_to_copy:
        print("No content selected to copy.", file=sys.stderr)
        sys.exit(0)
    try:
        process = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True, stderr=subprocess.PIPE)
        _stdout, stderr = process.communicate(input=content_to_copy)
        if process.returncode != 0:
            print(f"Error: Failed to copy to clipboard. STDERR: {stderr}", file=sys.stderr)
            sys.exit(1)
        print(
            f"Successfully copied lines {start_line} to {(end_line if end_line is not None else 'end')} of '{filename}' to clipboard."
        )
    except FileNotFoundError:
        print("Error: 'termux-clipboard-set' command not found. Is Termux:API installed?", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while copying to clipboard: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(f"Usage: {sys.argv[0]} <filename> <start_line> [end_line]", file=sys.stderr)
        print("  <filename>: Path to the input file.", file=sys.stderr)
        print("  <start_line>: The first line number to copy (1-based index).", file=sys.stderr)
        print(
            "  [end_line]: The last line number to copy (1-based index). If omitted, copies to the end of the file.",
            file=sys.stderr,
        )
        sys.exit(1)
    filename = sys.argv[1]
    try:
        start_line = int(sys.argv[2])
    except ValueError:
        print("Error: <start_line> must be an integer.", file=sys.stderr)
        sys.exit(1)
    end_line = None
    if len(sys.argv) == 4:
        try:
            end_line = int(sys.argv[3])
        except ValueError:
            print("Error: <end_line> must be an integer.", file=sys.stderr)
            sys.exit(1)
    copy_lines_to_clipboard(filename, start_line, end_line)


if __name__ == "__main__":
    main()
