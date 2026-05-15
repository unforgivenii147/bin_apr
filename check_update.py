#!/data/data/com.termux/files/usr/bin/python

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

import json
import sys
import time

import requests
from dh import get_installed_packages
from packaging.version import InvalidVersion, Version


def check_package_on_pypi(package_name: str, current_version: str) -> str | None:
    try:
        time.sleep(0.01)
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
        if response.status_code == 404:
            return None
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Error checking {package_name}: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"  ⚠️  Error parsing response for {package_name}: {e}")
        return None


def compare_versions(current: str, latest: str) -> str:
    try:
        current_v = Version(current)
        latest_v = Version(latest)
        if current_v < latest_v:
            return "update"
        if current_v > latest_v:
            return "newer"
    except InvalidVersion:
        if current == latest:
            return "current"
        if current < latest:
            return "update"
        return "newer"


def is_venv() -> bool:
    return hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)


def main() -> None:
    if not is_venv():
        print("⚠️  Warning: Not running in a virtual environment!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            print("Exiting.")
            return
    print("📦 Checking for package updates on PyPI...")
    print("(Results will appear as each package is checked)\n")
    installed = get_installed_packages()
    total_packages = len(installed)
    print(f"Processing {total_packages} packages:\n")
    updates_found = []
    errors = []
    up_to_date = 0
    for i, (package, current_version) in enumerate(sorted(installed.items()), 1):
        progress = f"[{i:3d}/{total_packages:3d}]"
        latest_version = check_package_on_pypi(package.lower(), current_version)
        if latest_version is None:
            print(f"{progress} {package:<30} : ⚠️  not found on PyPI")
            errors.append(package)
            continue
        status = compare_versions(current_version, latest_version)
        if status == "update":
            print(f"{progress} {package:<30} : 📦 update available from {current_version} to {latest_version}")
            updates_found.append((package, current_version, latest_version))
        elif status == "newer":
            print(
                f"{progress} {package:<30} : ⚠️  current version ({current_version}) is newer than PyPI ({latest_version})"
            )
            errors.append(package)
        else:
            print(f"{progress} {package:<30} : ✅ already latest version ({current_version})")
            up_to_date += 1
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total packages checked: {total_packages}")
    print(f"✅ Up to date: {up_to_date}")
    print(f"📦 Updates available: {len(updates_found)}")
    print(f"⚠️  Errors/Not found: {len(errors)}")
    if updates_found:
        print("\n" + "=" * 60)
        print("PACKAGES TO UPDATE")
        print("=" * 60)
        for package, current, latest in updates_found:
            print(f"  {package:<30} {current} -> {latest}")
        print("\n💡 To upgrade all packages, run:")
        packages_to_upgrade = [p[0] for p in updates_found]
        print(f"   python -m pip install --upgrade {' '.join(packages_to_upgrade)}")
        print("\n💡 To upgrade a specific package, run:")
        print("   python -m pip install --upgrade <package-name>")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
