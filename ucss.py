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

import base64
import hashlib
import mimetypes
import re
import sys
from pathlib import Path

from dh import MIME_TO_EXT

DATA_URL_RE = re.compile(
    "url\\(\\s*(['\\\"]?)data:(?P<mime>application/(?:vnd\\.ms-fontobject|font-[^;]+|font/[^;]+))(?:;charset=[^;]+)?;base64,(?P<data>[A-Za-z0-9+/=\\s]+)\\1\\s*\\)",
    re.IGNORECASE,
)
MIME_FALLBACKS = MIME_TO_EXT


def ext_from_mime(mime: str) -> str:
    ext = mimetypes.guess_extension(mime)
    if ext:
        return ext
    return MIME_FALLBACKS.get(mime, ".bin")


def extract_css_base64(css_path: Path, out_dir: Path):
    css = css_path.read_text(encoding="utf-8", errors="ignore")
    out_dir.mkdir(exist_ok=True)
    seen = {}

    def replace(match):
        mime = match.group("mime")
        raw = match.group("data").replace("\n", "").strip()
        binary = base64.b64decode(raw)
        sha = hashlib.sha256(binary).hexdigest()[:12]
        if sha not in seen:
            ext = ext_from_mime(mime)
            fname = f"asset-{sha}{ext}"
            (out_dir / fname).write_bytes(binary)
            seen[sha] = fname
        return f"url('{out_dir.name}/{seen[sha]}')"

    new_css = DATA_URL_RE.sub(replace, css)
    if new_css != css:
        css_path.write_text(new_css, encoding="utf-8")
    return len(seen)


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_css_base64.py file1.css [file2.css ...]")
        sys.exit(1)
    out_dir = Path("_static")
    total = 0
    for css_file in map(Path, sys.argv[1:]):
        if not css_file.exists():
            print(f"skip: {css_file}")
            continue
        count = extract_css_base64(css_file, out_dir)
        total += count
        print(f"{css_file}: extracted {count} assets")
    print(f"\nTotal saved assets: {total}")
    print(f"Output directory: ./{out_dir}")


if __name__ == "__main__":
    main()
