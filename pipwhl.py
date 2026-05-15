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

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

LOCAL_MIRROR_URL = "https://mirror-pypi.runflare.com"


def download_file(url, dest_folder="."):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        filepath = os.path.join(dest_folder, filename)
        with Path(filepath).open("wb") as f:
            f.writelines(response.iter_content(chunk_size=8192))
        print(f"Downloaded: {filename}")
        return filepath
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None


def get_package_info_from_mirror(package_name):
    mirror_package_url = f"{LOCAL_MIRROR_URL}/{package_name}"
    print(f"Fetching package info from mirror: {mirror_package_url}")
    try:
        response = requests.get(mirror_package_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        wheel_urls = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.endswith(".whl"):
                full_url = f"{LOCAL_MIRROR_URL}{href}" if href.startswith("/") else href
                wheel_urls.append(full_url)
        if not wheel_urls:
            print(f"No .whl files found for {package_name} on the mirror.")
            return None
        print(f"Found wheel URLs for {package_name}: {wheel_urls}")
        return wheel_urls[0]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from mirror {mirror_package_url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while parsing mirror response: {e}")
        return None


def install_or_download(package_name):
    print(f"Checking for package: {package_name}")
    wheel_url = get_package_info_from_mirror(package_name)
    if wheel_url:
        print(f"Wheel found for {package_name} at {wheel_url}. Installing...")
        try:
            install_command = [sys.executable, "-m", "pip", "install", wheel_url]
            subprocess.run(install_command, check=True)
            print(f"Successfully installed {package_name} from wheel.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package_name} from {wheel_url}: {e}")
            print(f"Installation failed for {package_name}. Could not find a source archive fallback from mirror.")
    else:
        print(f"No wheel found for {package_name} on the mirror.")
        print("This script currently only handles wheel installations from the mirror.")
        print(
            "If a source archive (.tar.gz or .zip) were available and desired, additional parsing logic would be needed."
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pip_wrapper.py <package_name1> [package_name2 ...]")
        sys.exit(1)
    packages_to_process = sys.argv[1:]
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("The 'beautifulsoup4' library is required. Please install it: pip install beautifulsoup4")
        sys.exit(1)
    for pkg in packages_to_process:
        install_or_download(pkg)
