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

import re
import sys
from pathlib import Path

from dh import atomic_write

LOCAL_FONT_BASE = Path("/sdcard/_static/fonts")
FONT_EXTS = {".woff", ".woff2", ".ttf", ".otf", ".eot"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
IMPORT_RE = re.compile("@import\\s+url\\([^)]+fonts\\.googleapis[^)]+\\);?", re.IGNORECASE)
FAMILY_RULES = {
    "roboto": "roboto",
    "lato": "lato",
    "opensans": "opensans",
    "open-sans": "opensans",
    "fontawesome": "fa",
    "fa-": "fa",
}
URL_RE = re.compile("url\\(([\"\\']?)(https?://[^)]+?\\.(?:woff2?|ttf|otf|eot))\\1\\)", re.IGNORECASE)


def find_css(paths):
    seen = set()
    result = []
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix.lower() == ".css":
            rp = p.resolve()
            if rp not in seen:
                seen.add(rp)
                result.append(rp)
        elif p.is_dir():
            pattern = "**/*.css"
            for f in sorted(p.glob(pattern)):
                rp = f.resolve()
                if rp not in seen:
                    seen.add(rp)
                    result.append(rp)
        else:
            print(f"Skipping invalid path: {p}", file=sys.stderr)
    return result


def read_css(files):
    charset_line = None
    chunks = []

    def localize_font_url(match):
        url = match.group(2)
        filename = url.split("/")[-1]
        return f'url("{LOCAL_FONT_BASE}/{filename}")'

    for file in files:
        text = file.read_text(errors="ignore")
        text = IMPORT_RE.sub("", text)
        text = URL_RE.sub(localize_font_url, text)
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith("@charset"):
                if charset_line is None:
                    charset_line = line.strip()
                continue
            cleaned.append(line)
        chunks.append((file, "\n".join(cleaned).strip()))
    return (charset_line, chunks)


def join_css(files, output):
    charset, chunks = read_css(files)
    parts = []
    if charset:
        parts.append(charset + "\n")
    for file, content in chunks:
        parts.append(f"\n/* ===== {file.name} ===== */\n{content}\n")
    final_css = "\n".join(parts).strip() + "\n"
    atomic_write(output, final_css)


def main():
    files = find_css(".")
    if not files:
        print("No CSS files found.", file=sys.stderr)
        sys.exit(1)
    join_css(files, "merged.css")
    print(f"Joined {len(files)} files -> merged.css")


if __name__ == "__main__":
    main()
