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
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import argparse
import json
import os
import signal
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager, cpu_count

DEFAULT_URL = "https://sr.moviesho.com/Series/"
STATE_FILE = "crawler_state.json"
TXT_OUTPUT = "movies.txt"
JSON_OUTPUT = "movies.json"

stop_flag = False


# ----------------------------
# Signal Handling
# ----------------------------
def signal_handler(sig, frame):
    global stop_flag
    print("\n⚠️  Interrupt received! Saving progress...")
    stop_flag = True


signal.signal(signal.SIGINT, signal_handler)


# ----------------------------
# Helpers
# ----------------------------
def size_to_mb(size_str):
    match = re.search(r"([\d.]+)\s*Mi?B", size_str)
    if match:
        return float(match.group(1))
    return None


def extract_quality(filename):
    if "480p" in filename.lower():
        return "480"
    if "720p" in filename.lower():
        return "720"
    return None


def fetch_directory(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def parse_directory(url, max_size):
    results = []
    subdirs = []

    html = fetch_directory(url)
    if not html:
        return results, subdirs

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        link_tag = cols[0].find("a")
        if not link_tag:
            continue

        name = link_tag.text.strip()
        href = link_tag.get("href")
        size_text = cols[1].text.strip()

        if "Parent directory" in name:
            continue

        full_url = urljoin(url, href)

        # Directory
        if href.endswith("/"):
            subdirs.append(full_url)
            continue

        # File
        if not name.lower().endswith(".mkv"):
            continue

        quality = extract_quality(name)
        if quality not in ("480", "720"):
            continue

        size_mb = size_to_mb(size_text)
        if size_mb is None or size_mb > max_size:
            continue

        results.append({"url": full_url, "quality": quality, "size_mb": size_mb})

    return results, subdirs


# ----------------------------
# Save & Resume
# ----------------------------
def save_state(queue, visited):
    state = {"queue": list(queue), "visited": list(visited)}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


def load_state():
    if not os.path.exists(STATE_FILE):
        return None, None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    return set(state["visited"]), state["queue"]


def append_results(results):
    # Append to txt
    with open(TXT_OUTPUT, "a", encoding="utf-8") as f:
        for r in results:
            f.write(r["url"] + "\n")

    # Append to JSON (line-based JSON)
    with open(JSON_OUTPUT, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")


# ----------------------------
# Main Crawl Logic
# ----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default=DEFAULT_URL, help="Base URL to crawl")
    parser.add_argument("-s", "--size", type=float, default=300, help="Max size in MB (default 300)")
    args = parser.parse_args()

    max_size = args.size
    base_url = args.url if args.url.endswith("/") else args.url + "/"

    manager = Manager()
    visited = manager.list()
    queue = manager.list()

    # Resume support
    prev_visited, prev_queue = load_state()

    if prev_queue:
        print("🔁 Resuming previous crawl...")
        visited[:] = prev_visited
        queue[:] = prev_queue
    else:
        queue.append(base_url)

    workers = cpu_count()
    print(f"🚀 Using {workers} processes")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        while queue and not stop_flag:
            futures = {}

            # Submit batch
            for _ in range(min(len(queue), workers)):
                url = queue.pop(0)
                if url in visited:
                    continue
                visited.append(url)
                futures[executor.submit(parse_directory, url, max_size)] = url

            for future in as_completed(futures):
                if stop_flag:
                    break

                results, subdirs = future.result()

                if results:
                    append_results(results)
                    print(f"✅ Found {len(results)} movies")

                for sub in subdirs:
                    if sub not in visited:
                        queue.append(sub)

    # Save state before exit
    save_state(queue, visited)

    if stop_flag:
        print("💾 Progress saved. Run again to continue.")
    else:
        # Cleanup state if finished
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        print("✅ Crawl completed successfully.")


if __name__ == "__main__":
    main()
