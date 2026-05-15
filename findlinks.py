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
"""
Search a website for [ext] files and save their URLs to urls.txt.
Usage:
    python find_[ext]s.py <start_url> [max_pages] [delay_seconds]
Example:
    python find_[ext]s.py https://example.com/docs 100 0.5
"""

import sys
import time
import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from collections import deque


def can_fetch(rp, url):
    """Check if crawling is allowed for `url` by robots.txt."""
    try:
        return rp.can_fetch("*", url)
    except Exception:
        return True  # Assume allowed if robots.txt parsing fails


def crawl_for_ext(start_url, max_pages, delay, ext):
    parsed = urlparse(start_url)
    if not parsed.scheme:
        start_url = "https://" + start_url.lstrip("/")
        parsed = urlparse(url)
    base_netloc = parsed.netloc
    rp = RobotFileParser()
    robots_url = urljoin(start_url, "/robots.txt")
    try:
        rp.set_url(robots_url)
        rp.read()
        print(f"✅ Loaded robots.txt: {robots_url}")
    except Exception as e:
        print(f"⚠️  Could not load robots.txt ({e}). Proceeding with caution.")
        rp = None
    visited = set()
    found_urls = set()
    queue = deque([start_url])
    headers = {"User-Agent": "EXT-Crawler/1.0 (non-commercial; see --help)"}
    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        if rp and not can_fetch(rp, url):
            print(f"🚫 Skipping (robots.txt): {url}")
            continue
        visited.add(url)
        try:
            print(f"🔍 Checking: {url}")
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "").lower()
            if ext in content_type:
                found_urls.add(url)
                print(f"  📄 (via Content-Type): {url}")
                continue
            if "html" not in content_type and not url.lower().endswith((".html", ".htm")):
                continue
            soup = BeautifulSoup(resp.content, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                full_url = urljoin(url, href)
                if not full_url.startswith(("http://", "https://")):
                    continue
                if urlparse(full_url).netloc != base_netloc:
                    continue
                if full_url.lower().endswith(ext):
                    found_urls.add(full_url)
                    print(f"  📄found {ext} (via link): {full_url}")
                elif full_url not in visited:
                    # Queue for crawling (only HTML-like pages)
                    if not any(
                        full_url.lower().endswith(extension)
                        for extension in (".jpg", ".jpeg", ".png", ".gif", ".css", ".js")
                    ):
                        queue.append(full_url)
        except requests.RequestException as e:
            print(f"  ⚠️  Request error: {e}")
        except Exception as e:
            print(f"  ⚠️  Unexpected error: {e}")
        time.sleep(delay)
    return sorted(found_urls)


def save_urls(urls, filename="urls.txt"):
    """Save URLs to a file, one per line."""
    with open(filename, "w", encoding="utf-8") as f:
        for url in urls:
            f.write(url + "\n")
    print(f"\n✅ Saved {len(urls)} URLs to '{filename}'")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    start_url = sys.argv[1]
    ext = sys.argv[2]
    max_pages = 1000
    delay = 1.0
    ext_urls = crawl_for_ext(start_url, max_pages, delay, ext)
    save_urls(ext_urls)


if __name__ == "__main__":
    main()
