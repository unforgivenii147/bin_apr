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
import mmap
import os
import random
import secrets
from pathlib import Path


def enhanced_shuffle(input_file, output_file_prefix=None, methods=None, repeats=3):
    if methods is None:
        methods = ["basic", "crypto", "shuffle3"]
    input_file_path = Path(input_file)
    file_size = input_file_path.stat().st_size
    print(f"Read {file_size} bytes from {input_file}")
    lines = []
    if file_size > 5 * 1024 * 1024:
        print("File size > 5MB, attempting to use mmap.")
        try:
            with Path(input_file).open("r+b") as f:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                decoded_content = mm.decode("utf-8", errors="ignore")
                lines = decoded_content.splitlines(keepends=True)
                mm.close()
        except Exception as e:
            print(f"Error using mmap: {e}. Falling back to standard file reading.")
            with Path(input_file).open(encoding="utf-8") as f:
                lines = f.readlines()
    else:
        with Path(input_file).open(encoding="utf-8") as f:
            lines = f.readlines()
    original_count = len(lines)
    print(f"Read {original_count} lines from {input_file}")
    for method in methods:
        print(f"\n--- Shuffling with method: {method} ---")
        shuffled_lines = lines.copy()
        for _ in range(repeats):
            if method == "basic":
                random.shuffle(shuffled_lines)
            elif method == "crypto":
                crypto_shuffle(shuffled_lines)
            elif method == "shuffle3":
                shuffle3(shuffled_lines)
        output_path = output_file_prefix or input_file
        if output_file_prefix:
            output_path = f"{output_file_prefix}_{method}.txt"
        else:
            base, ext = os.path.splitext(input_file)
            output_path = f"{base}_{method}{ext}"
        with Path(output_path).open("w", encoding="utf-8") as f:
            f.writelines(shuffled_lines)
        print(f"Shuffled {original_count} lines using method '{method}' with {repeats} passes")
        print(f"Output written to: {output_path}")


def crypto_shuffle(lst):
    for i in range(len(lst) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        lst[i], lst[j] = (lst[j], lst[i])


def shuffle3(lst):
    sys_random = random.SystemRandom()
    for i in range(len(lst) - 1, 0, -1):
        j = sys_random.randint(0, i)
        lst[i], lst[j] = (lst[j], lst[i])


def test_randomness(input_file):
    method_to_test = "crypto"
    print(f"Testing randomness with method: {method_to_test}")
    lines_to_test = []
    try:
        with Path(input_file).open(encoding="utf-8") as f:
            lines_to_test = [line.strip() for line in f.readlines()[:100]]
    except Exception as e:
        print(f"Error reading file for testing: {e}")
        return
    if not lines_to_test:
        print("No lines found to test.")
        return
    original_order = lines_to_test.copy()
    for i in range(5):
        current_lines = original_order.copy()
        if method_to_test == "basic":
            random.shuffle(current_lines)
        elif method_to_test == "crypto":
            crypto_shuffle(current_lines)
        elif method_to_test == "shuffle3":
            shuffle3(current_lines)
        changes = sum((1 for a, b in zip(original_order, current_lines, strict=False) if a != b))
        print(f"Shuffle {i + 1}: {changes} out of {len(current_lines)} positions changed")


def main():
    parser = argparse.ArgumentParser(description="Randomize lines in a file")
    parser.add_argument("input_file", help="Input file to shuffle")
    parser.add_argument(
        "-o", "--output", help="Output file prefix (default: will append method name to input file name)"
    )
    parser.add_argument("-r", "--repeats", type=int, default=3, help="Number of shuffle passes per method (default: 3)")
    parser.add_argument("-t", "--test", action="store_true", help="Test randomness of the 'crypto' method")
    args = parser.parse_args()
    output_prefix = args.output
    if output_prefix and (not output_prefix.endswith((".txt", ".TXT"))):
        output_prefix += ".txt"
    if args.test:
        test_randomness(args.input_file)
    else:
        enhanced_shuffle(args.input_file, output_prefix, methods=["basic", "crypto", "shuffle3"], repeats=args.repeats)


if __name__ == "__main__":
    main()
