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

import importlib
import subprocess
import sys

import pkg_resources


def get_installed_python_packages() -> list[tuple[str, str]]:
    return [(d.project_name, d.version) for d in pkg_resources.working_set]


def check_package_importable(package_name: str) -> tuple[bool, str]:
    try:
        importlib.import_module(package_name)
        return (True, "OK")
    except ImportError as e:
        return (False, f"ImportError: {e}")
    except Exception as e:
        return (False, f"Unexpected error: {e}")


def get_latest_version(package_name: str) -> str:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", f"{package_name}==", "--dry-run"],
            capture_output=True,
            text=True,
            check=True,
        )
        match = re.search("would be installed \\(([^)]+)\\)", result.stdout)
        if match:
            return match.group(1)
    except subprocess.CalledProcessError:
        pass
    return "Unknown"


def main():
    print("=== Python Packages Sanity Check ===")
    installed_pkgs = get_installed_python_packages()
    print(f"Found {len(installed_pkgs)} installed Python packages.\n")
    issues_found = 0
    for pkg_name, pkg_version in installed_pkgs:
        is_ok, msg = check_package_importable(pkg_name)
        if not is_ok:
            print(f"[!] {pkg_name} (v{pkg_version}): {msg}")
            issues_found += 1
    print("\n=== Version Check (Optional) ===")
    print("Checking for outdated packages (this may take a while)...")
    outdated_pkgs = []
    for pkg_name, pkg_version in installed_pkgs:
        latest_version = get_latest_version(pkg_name)
        if latest_version not in {"Unknown", pkg_version}:
            outdated_pkgs.append((pkg_name, pkg_version, latest_version))
    if outdated_pkgs:
        print("Outdated packages found:")
        for pkg_name, pkg_version, latest_version in outdated_pkgs:
            print(f"- {pkg_name}: {pkg_version} (latest: {latest_version})")
    else:
        print("All packages are up to date.")
    print("\n=== Summary ===")
    print(f"Issues found: {issues_found}")
    if issues_found == 0:
        print("All packages are importable.")
    else:
        print("Some packages may need attention.")


if __name__ == "__main__":
    main()
