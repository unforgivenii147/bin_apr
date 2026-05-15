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

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


def has_native_wheels(info) -> bool:
    urls = info.get("urls", [])
    for u in urls:
        filename = u.get("filename", "").lower()
        if any((ext in filename for ext in [".so", ".pyd", ".dll", "win_amd64", "manylinux", "macosx"])):
            return True
    return False


def check_package(name) -> tuple:
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return (name, "not_found")
        info = resp.json()
        if has_native_wheels(info):
            return (name, "native")
        return (name, "pure")
    except Exception:
        return (name, "not_found")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python detect_pure_python.py <package_list.txt>")
        sys.exit(1)
    infile = sys.argv[1]
    pure = set()
    native = set()
    missing = set()
    with Path(infile).open(encoding="utf-8") as f:
        packages = [line.strip() for line in f if line.strip()]
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_package, pkg): pkg for pkg in packages}
        for future in as_completed(futures):
            pkg, result = future.result()
            if result == "pure":
                pure.add(pkg)
            elif result == "native":
                native.add(pkg)
            else:
                missing.add(pkg)
    Path("pure_python.txt").write_text("\n".join(sorted(pure)), encoding="utf-8")
    Path("native_extensions.txt").write_text("\n".join(sorted(native)), encoding="utf-8")
    Path("not_found.txt").write_text("\n".join(sorted(missing)), encoding="utf-8")
    print("Done!")
    print(f"Pure Python: {len(pure)}")
    print(f"Native-required: {len(native)}")
    print(f"Not found: {len(missing)}")


if __name__ == "__main__":
    main()
