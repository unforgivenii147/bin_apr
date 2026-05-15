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
import operator
import os
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


def scan_directory(path="."):
    total_size = 0
    file_count = 0
    folder_count = 0
    extensions = set()
    size_by_ext = defaultdict(int)
    for root, dirs, files in os.walk(path):
        folder_count += len(dirs)
        for filename in files:
            file_count += 1
            full_path = Path(root) / filename
            try:
                size = full_path.stat().st_size
            except OSError:
                size = 0
            total_size += size
            ext = full_path.suffix
            ext = ext.lower() if ext else "(no extension)"
            extensions.add(ext)
            size_by_ext[ext] += size
    return (total_size, file_count, folder_count, extensions, size_by_ext)


def format_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_in_bytes / 1024**3:.2f} GB"


def write_summary(filename: Path | None = None) -> None:
    total_size, file_count, folder_count, extensions, size_by_ext = scan_directory()
    summary_lines = []
    summary_lines.append(f"Total size: {format_size(total_size)}\n")
    summary_lines.append("File extensions:\n")
    sorted_extensions = sorted(list(extensions))
    for ext in sorted_extensions:
        summary_lines.append(f"   - {ext}\n")
    summary_lines.append(f"Number of files: {file_count}\n")
    summary_lines.append(f"Number of folders: {folder_count}\n")
    summary_lines.append("Size by extension:\n")
    sorted_size_by_ext = sorted(size_by_ext.items(), key=operator.itemgetter(1), reverse=True)
    for ext, size in sorted_size_by_ext:
        summary_lines.append(f"  {ext}: {format_size(size)}\n")
        if filename is None or filename == sys.stderr:
            print(f"  {ext}: {format_size(size)}\n", file=sys.stderr)
    summary_string = "".join(summary_lines)
    if filename and filename != sys.stderr:
        try:
            with filename.open("w", encoding="utf-8") as f:
                f.write(summary_string)
            print(f"Summary saved to {filename}")
        except IOError as e:
            print(f"Error saving summary to {filename}: {e}", file=sys.stderr)
    elif filename is None:
        print(summary_string)


def create_bar_chart(chart_type: str, output_filename: str = "dirinfo.png") -> None:
    _, _, _, _, size_by_ext = scan_directory()
    sorted_items = sorted(
        [(ext, size) for ext, size in size_by_ext.items() if size > 0], key=operator.itemgetter(1), reverse=True
    )
    if not sorted_items:
        print("No data to plot.", file=sys.stderr)
        return
    extensions, sizes = zip(*sorted_items)
    reshaped_extensions = extensions
    plt.title("Size by File Extension")
    plt.xticks(rotation=45, ha="right")
    plt.gca().set_xticklabels(reshaped_extensions)
    plt.figure(figsize=(12, 7))
    plt.bar(reshaped_extensions, sizes, color="skyblue")
    plt.xlabel("File Extension")
    plt.ylabel("Size (bytes)")
    plt.tight_layout()
    try:
        plt.savefig(output_filename)
        print(f"Bar chart saved to {output_filename}")
    except Exception as e:
        print(f"Error saving chart to {output_filename}: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze directory information.")
    parser.add_argument(
        "-s", "--save", action="store_true", help="Save the report to a file named .dirinfo in the current directory."
    )
    parser.add_argument(
        "-i",
        "--image",
        metavar="FILENAME",
        type=str,
        help="Save a Matplotlib bar chart of file types and sizes to the specified image file (e.g., chart.png).",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=["persian", "english"],
        default="english",
        help="Specify the language/type of the Matplotlib chart title and labels (default: english).",
    )
    parser.add_argument(
        "path",
        metavar="PATH",
        type=str,
        nargs="?",
        default=".",
        help="The directory to scan (default: current directory).",
    )
    args = parser.parse_args()
    if args.save:
        write_summary(Path(".dirinfo"))
    elif args.image:
        create_bar_chart(args.type, args.image)
    else:
        write_summary()
