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
import sys

import matplotlib.pyplot as plt

MAX_DIRS = 25
MIN_SIZE_KB = 100
OUTPUT_FILENAME = "dirinfo.png"
CHART_TYPE = "bar"


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    size_kb = size_bytes / 1024
    if size_kb < 1024:
        return f"{size_kb:.2f} KB"
    size_mb = size_kb / 1024
    if size_mb < 1024:
        return f"{size_mb:.2f} MB"
    size_gb = size_mb / 1024
    return f"{size_gb:.2f} GB"


def get_dir_size(start_path):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    try:
                        total_size += os.path.getsize(fp)
                    except OSError:
                        pass
    except Exception as e:
        print(f"Error walking directory {start_path}: {e}", file=sys.stderr)
    return total_size


def create_chart(target_dir="."):
    target_dir = os.path.abspath(target_dir)
    print(f"Analyzing directory: {target_dir}")
    subdir_sizes = {}
    total_size = 0
    try:
        for entry in os.scandir(target_dir):
            if entry.is_dir() and (not entry.name.startswith(".")) and (not os.path.islink(entry.path)):
                size = get_dir_size(entry.path)
                if size >= MIN_SIZE_KB * 1024:
                    subdir_sizes[entry.name] = size
                    total_size += size
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return
    if not subdir_sizes:
        print("No subdirectories meeting criteria.")
        return
    sorted_subdirs = sorted(subdir_sizes.items(), key=lambda item: item[1], reverse=True)
    top_subdirs = dict(sorted_subdirs[:MAX_DIRS])
    remaining_size = sum((size for name, size in subdir_sizes.items() if name not in top_subdirs))
    percentages = {name: size / total_size * 100 for name, size in top_subdirs.items()}
    if remaining_size > 0:
        percentages["Other"] = remaining_size / total_size * 100
    labels = list(top_subdirs.keys())
    if remaining_size > 0:
        labels.append("Other")
    sizes = list(percentages.values())
    fig, ax = plt.subplots(figsize=(10, 6))
    if CHART_TYPE == "bar":
        ax.bar(labels, sizes, color="skyblue")
        ax.set_ylabel("Percentage %")
        ax.set_title("Directory Size Distribution")
    elif CHART_TYPE == "pie":
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        ax.set_title("Directory Size Distribution")
    elif CHART_TYPE == "circle":
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, wedgeprops=dict(width=0.4))
        ax.set_title("Directory Size Distribution")
    else:
        print(f"Chart type '{CHART_TYPE}' is not supported.")
        return
    plt.tight_layout()
    try:
        plt.savefig(OUTPUT_FILENAME, dpi=300)
        print(f"Chart saved to {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"Error saving chart: {e}", file=sys.stderr)
    plt.close()


if __name__ == "__main__":
    create_chart()
