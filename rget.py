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
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from tqdm import tqdm

MAX_WORKERS = 8
MAX_RETRIES = 3
TIMEOUT = 60
OUTPUT_DIR = "downloads"
URLS_FILE = "urls.txt"
SAFE_EXTENSIONS = [
    "\\.ttf$",
    "\\.woff$",
    "\\.woff2$",
    "\\.eot$",
    "\\.otf$",
    "\\.min\\.css$",
    "\\.min\\.js$",
    "\\.css$",
    "\\.js$",
    "\\.pdf$",
    "\\.html?$",
    "\\.whl$",
    "\\.tar\\.(gz|xz|zst|bz2|lzma|7z)$",
    "\\.zip$",
]
EXT_PATTERN = re.compile("|".join(SAFE_EXTENSIONS), re.IGNORECASE)


def sanitize_filename(name):
    name = unquote(name)
    name = re.sub('[<>:"|?*]', "_", name)
    return name[:255].strip() or "downloaded_file"


def extract_filename(url):
    parsed = urlparse(url)
    path = parsed.path
    filename = path.split("/")[-1] or "index.html"
    filename = filename.split("#")[0]
    filename = filename.split("?")[0]
    filename = sanitize_filename(filename)
    if not re.search("\\.[a-zA-Z0-9]+$", filename):
        filename += ".dat"
    return filename


def is_safe_extension(url):
    parsed = urlparse(url)
    path = parsed.path
    filename = path.split("/")[-1]
    base_name = filename.split("?")[0].split("#")[0]
    return bool(EXT_PATTERN.search(base_name))


def get_filesize(url, session):
    try:
        r = session.head(url, timeout=TIMEOUT, allow_redirects=True)
        r.raise_for_status()
        size = r.headers.get("Content-Length")
        return int(size) if size else None
    except Exception:
        return None


def download_one(url, session, output_dir, resume_from=None):
    filename = extract_filename(url)
    filepath = os.path.join(output_dir, filename)
    offset = 0
    if resume_from and Path(filepath).exists():
        offset = Path(filepath).stat().st_size
        remote_size = get_filesize(url, session)
        if remote_size is not None and offset >= remote_size:
            return (url, True, f"Already complete ({offset} bytes)")
    headers = {}
    if offset > 0:
        headers["Range"] = f"bytes={offset}-"
    try:
        with session.get(url, timeout=TIMEOUT, headers=headers, stream=True) as r:
            r.raise_for_status()
            content_length = int(r.headers.get("Content-Length", 0))
            total_size = content_length + offset if content_length else None
            mode = "ab" if offset else "wb"
            with Path(filepath).open(mode) as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
        return (url, True, filepath)
    except requests.exceptions.RequestException as e:
        if MAX_RETRIES > 0:
            return (url, False, f"Retry needed: {e}")
        return (url, False, str(e))


def download_urls(urls, output_dir=OUTPUT_DIR):
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    safe_urls = [url for url in urls if is_safe_extension(url)]
    skipped = len(urls) - len(safe_urls)
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} URLs (not matching safe extensions).")
    if not safe_urls:
        print("❌ No valid URLs to download.")
        return
    print(f"🚀 Starting download of {len(safe_urls)} URLs...\n")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; ResumableDownloader/1.0)"})
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(download_one, url, session, output_dir): url for url in safe_urls}
        with tqdm(total=len(safe_urls), desc="Downloading", unit="file") as pbar:
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    url, success, result = future.result()
                    if success:
                        pbar.write(f"✅ {url.split('?')[0]} → {result}")
                    else:
                        pbar.write(f"❌ {url.split('?')[0]} failed: {result}")
                except Exception as e:
                    pbar.write(f"⚠️  Unexpected error for {url}: {e}")
                pbar.update(1)
    session.close()


if __name__ == "__main__":
    try:
        with Path(URLS_FILE).open("r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and (not line.startswith("#"))]
    except FileNotFoundError:
        print(f"❌ Error: {URLS_FILE} not found.")
        sys.exit(1)
    if not urls:
        print(f"⚠️  No URLs found in {URLS_FILE}.")
        sys.exit(0)
    if len(sys.argv) > 1:
        URLS_FILE = sys.argv[1]
        print(f"Using input file: {URLS_FILE}")
        download_urls(urls)
    print("\n✅ All downloads completed.")
