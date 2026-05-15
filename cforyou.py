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

import contextlib
import json
import re
import time
from pathlib import Path

import requests
from dh import get_installed_packages
from packaging.version import Version
from termcolor import cprint

MAX_WORKERS = 8
TIMEOUT = 15
RESULTS_FILE = "/sdcard/c4u.json"


def save_output(text, pkg):
    Path(f"/sdcard/whl/json/{pkg}.html").write_text(text, encoding="utf-8")


def get_latest_version(pkg_name: str) -> str | None:
    url = f"https://mirror-pypi.runflare.com/{pkg_name}/json"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        html = response.text
        save_output(html, pkg_name)
        cprint(f"/sdcard/whl/json/{pkg_name}.html created")
    except:
        return None
    wheel_pattern = re.compile(
        f"{re.escape(pkg_name)}-([0-9][A-Za-z0-9\\.\\-_]*)\\.(?:whl|tar\\.gz|zip)", re.IGNORECASE
    )
    versions = []
    print(html[:-100])
    for match in wheel_pattern.finditer(html):
        version_str = match.group(1)
        with contextlib.suppress(BaseException):
            versions.append(Version(version_str))
    max_ver = str(max(versions)) if versions else None
    if max_ver is not None:
        print(f"{pkg_name}:{max_ver}")
    return max_ver


def load_previous_results() -> dict[str, dict]:
    if Path(RESULTS_FILE).exists():
        try:
            with Path(RESULTS_FILE).open(encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            cprint(f"Warning: Corrupted results file '{RESULTS_FILE}'. Starting fresh.", "red")
            return {}
    return {}


def save_results(results: dict[str, dict]):
    with Path(RESULTS_FILE).open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    start_time = time.time()
    installed_packages = get_installed_packages()
    total_packages = len(installed_packages)
    cprint(f"Found {total_packages} installed packages.", "blue")
    previous_results = load_previous_results()
    current_results = {}
    packages_to_check = []
    for pkg_name, installed_version in installed_packages.items():
        if pkg_name in previous_results:
            prev_data = previous_results[pkg_name]
            if prev_data.get("latest_version") and prev_data.get("latest_version") == "null":
                packages_to_check.append((pkg_name, installed_version))
                continue
            if prev_data.get("installed_version") == installed_version:
                current_results[pkg_name] = prev_data
                continue
        packages_to_check.append((pkg_name, installed_version))
    cprint(f"Will check {len(packages_to_check)} packages.", "blue")
    updatable_pkgs_info: list[tuple[str, str, str]] = []
    for i, (pkg_name, installed_version) in enumerate(packages_to_check):
        latest_version_str = get_latest_version(pkg_name)
        current_results[pkg_name] = {
            "installed_version": installed_version,
            "latest_version": latest_version_str,
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if latest_version_str:
            try:
                installed_ver = Version(installed_version)
                latest_ver = Version(latest_version_str)
                if installed_ver < latest_ver:
                    updatable_pkgs_info.append((pkg_name, installed_version, latest_version_str))
                    cprint(
                        f"[{i + 1}/{len(packages_to_check)}] {pkg_name}: {installed_version} -> {latest_version_str} (Updatable!)",
                        "green",
                    )
                else:
                    cprint(
                        f"[{i + 1}/{len(packages_to_check)}] {pkg_name}: {installed_version} (Latest: {latest_version_str})",
                        "white",
                    )
            except Exception as ver_err:
                cprint(
                    f"[{i + 1}/{len(packages_to_check)}] {pkg_name}: Could not parse versions '{installed_version}' or '{latest_version_str}': {ver_err}",
                    "yellow",
                )
        else:
            cprint(f"[{i + 1}/{len(packages_to_check)}] {pkg_name}: Could not get latest version from PyPI.", "yellow")
        if (i + 1) % 10 == 0 or i + 1 == len(packages_to_check):
            save_results(current_results)
            cprint("Results saved periodically.", "blue")
    cprint("\n--- Summary of Updatable Packages ---", "blue")
    if updatable_pkgs_info:
        for pkg, installed_ver, latest_ver in updatable_pkgs_info:
            cprint(f"{pkg}: {installed_ver} -> {latest_ver}", "magenta")
        cprint(
            f"\nTo update these packages, you can use: pip install --upgrade {' '.join([p[0] for p in updatable_pkgs_info])}",
            "yellow",
        )
    else:
        cprint("All installed packages are up to date or could not be checked.", "green")
    end_time = time.time()
    cprint(f"\nFinished in {end_time - start_time:.2f} seconds.", "blue")
