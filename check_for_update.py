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

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def get_latest_version_info(pkg_name: str, mirror_url: str) -> dict:
    package_url = f"{mirror_url}/{pkg_name}"
    output_data = {
        "pkg_name": pkg_name,
        "latest_version": None,
        "url_of_latest_version": None,
        "html_content": None,
        "error": None,
    }
    try:
        response = requests.get(package_url)
        response.raise_for_status()
        output_data["html_content"] = response.text
        output_dir = "output"
        if not Path(output_dir).exists():
            Path(output_dir).mkdir(parents=True)
        Path(os.path.join(output_dir, f"{pkg_name}_debug.html")).write_text(response.text, encoding="utf-8")
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")
        if not links:
            output_data["error"] = "No links found for the package."
            return output_data
        latest_link_tag = links[-1]
        latest_url = latest_link_tag.get("href")
        if not latest_url:
            output_data["error"] = "Could not extract URL from the last link tag."
            return output_data
        full_latest_url = urljoin(mirror_url, latest_url)
        preferred_url = None
        sorted_links = sorted(
            links,
            key=lambda x: (
                ".tar.gz" not in x.get("href", ""),
                ".zip" not in x.get("href", ""),
                ".whl" not in x.get("href", ""),
            ),
        )
        for link_tag in sorted_links:
            href = link_tag.get("href")
            if href:
                if href.endswith(".tar.gz"):
                    preferred_url = urljoin(mirror_url, href)
                    break
                if href.endswith(".zip") or (href.endswith(".whl") and (not preferred_url)):
                    preferred_url = urljoin(mirror_url, href)
        if not preferred_url:
            output_data["error"] = "Could not find a preferred file type (.tar.gz, .zip, or .whl)."
            return output_data
        version_match = re.search("([\\w.-]+?)-(\\d+\\.\\d+(\\.\\d+)?(-\\w+)?).*\\.(tar\\.gz|zip|whl)", preferred_url)
        if version_match:
            output_data["latest_version"] = version_match.group(2)
        else:
            version_match_fallback = re.search("-(\\d+\\.\\d+(\\.\\d+)?(-\\w+)?)\\.", latest_url)
            if version_match_fallback:
                output_data["latest_version"] = version_match_fallback.group(1)
            else:
                output_data["error"] = "Could not extract version number from URL."
                return output_data
        output_data["url_of_latest_version"] = preferred_url
    except requests.exceptions.RequestException as e:
        output_data["error"] = f"Request error: {e}"
    except Exception as e:
        output_data["error"] = f"An unexpected error occurred: {e}"
    return output_data


def main():
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_package_list_file>")
        sys.exit(1)
    package_list_file = sys.argv[1]
    mirror_url = "https://mirror-pypi.runflare.com"
    output_json_file = "package_versions.json"
    all_results = []
    try:
        with Path(package_list_file).open("r", encoding="utf-8") as f:
            package_names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File not found at {package_list_file}")
        sys.exit(1)
    for pkg_name in package_names:
        print(f"Processing: {pkg_name}...")
        result = get_latest_version_info(pkg_name, mirror_url)
        all_results.append(result)
        try:
            with Path(output_json_file).open("w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=4, ensure_ascii=False)
        except OSError as e:
            print(f"Error writing to JSON file {output_json_file}: {e}")
    print(f"\nProcessing complete. Results saved to {output_json_file}")


if __name__ == "__main__":
    main()
