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
from urllib.parse import urlparse
import re
import sys
from pathlib import Path

INPUT_FILE = sys.argv[1]


def normalize_url(u: str) -> str:
    """Normalize a URL: ensure scheme, lowercase host, trim trailing slash on path (except root)."""
    u = u.strip()
    if not u:
        return ""
    if not re.match(r"^https?://", u, re.IGNORECASE):
        u = "https://" + u
    p = urlparse(u)
    scheme = p.scheme.lower()
    host = (p.netloc or "").lower()
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return f"{scheme}://{host}{path}"


def canonical_root(normalized: str) -> str:
    """
    Return the canonical root of a normalized URL:
      - GitHub: /owner/repo (ignores /issues, /tree, /blob, etc.)
      - Others: scheme://host/first_segment (or scheme://host/ if no path)
    """
    p = urlparse(normalized)
    scheme = p.scheme
    host = p.netloc.lower()
    if not host:
        return normalized

    if host in ("github.com", "www.github.com"):
        segs = [s for s in (p.path or "/").split("/") if s]
        if len(segs) >= 2:
            owner, repo = segs[0], segs[1]
            return f"https://github.com/{owner}/{repo}"
        return f"https://github.com"

    segs = [s for s in (p.path or "/").split("/") if s]
    if not segs:
        return f"{scheme}://{host}/"
    first = segs[0]
    return f"{scheme}://{host}/{first}"


def is_subsumed(candidate: str, existing: str) -> bool:
    """
    Check if `candidate` URL is a subpath of `existing` on the same host.
    Returns True if candidate is redundant (i.e., covered by existing).
    """
    cand_p = urlparse(candidate)
    ex_p = urlparse(existing)
    if cand_p.netloc.lower() != ex_p.netloc.lower():
        return False
    cand_path = (cand_p.path or "/").rstrip("/") or "/"
    ex_path = (ex_p.path or "/").rstrip("/") or "/"
    if cand_path == ex_path:
        return True
    if ex_path == "/" and cand_path != "/":
        return True
    if cand_path.startswith(ex_path + "/"):
        return True
    return False


def prune_subaddresses(urls):
    # Step 1: Normalize all and filter empties
    normalized = [normalize_url(u) for u in urls]
    normalized = [u for u in normalized if u]
    best_by_root = {}
    for n in normalized:
        root = canonical_root(n)
        if root not in best_by_root or len(n) < len(best_by_root[root]):
            best_by_root[root] = n
    kept = sorted(best_by_root.values(), key=len)
    final = []
    for cand in kept:
        # Skip if subsumed by any already-kept URL
        if any(is_subsumed(cand, k) for k in final):
            continue
        final.append(cand)
    final.sort()
    return final


def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{INPUT_FILE}': {e}", file=sys.stderr)
        sys.exit(1)
    pruned = prune_subaddresses(lines)
    try:
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            for url in pruned:
                f.write(url + "\n")
    except IOError as e:
        print(f"Error writing to file '{INPUT_FILE}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
