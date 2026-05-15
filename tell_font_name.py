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

from dh import get_files, mpf, unique_path
from fontTools.ttLib import TTFont
from termcolor import cprint


def is_ascii_printable(s: str) -> bool:
    return all((32 <= ord(c) <= 126 for c in s))


def clean_filename(s: str) -> str:
    s = re.sub("[^\\w\\-\\.]", "", s)
    return s.strip("_-.")


def get_best_name(font, name_id):
    fallback = None
    for rec in font["name"].names:
        if rec.nameID != name_id:
            continue
        try:
            name = rec.toUnicode().strip()
        except Exception:
            continue
        if rec.platformID == 3 and rec.langID == 1033:
            return name
        if is_ascii_printable(name):
            fallback = name
    return fallback


def get_font_names(path):
    font = TTFont(path)
    family = get_best_name(font, 1)
    subfamily = get_best_name(font, 2)
    if not family:
        return (None, None)
    family = clean_filename(family)
    subfamily = "Regular" if not subfamily else clean_filename(subfamily)
    if subfamily.lower() == family.lower():
        subfamily = "Regular"
    return (family, subfamily)


def process_file(fn):
    try:
        family, style = get_font_names(fn)
    except Exception as e:
        cprint(f"error: {e}", "magenta")
        return 1
    if not family:
        cprint("name not found", "magenta")
        return 1
    ext = fn.suffix.lower()
    new_path = fn.parent / f"{family}-{style}{ext}"
    if fn.name == new_path.name:
        cprint("no change", "blue")
        return 0
    new_path = Path(
        str(new_path)
        .replace("_1", "")
        .replace("_2", "")
        .replace("_3", "")
        .replace("_4", "")
        .replace("_5", "")
        .replace("_6", "")
        .replace("_7", "")
        .replace("_8", "")
        .replace("_9", "")
    )
    if new_path.exists():
        new_path = unique_path(new_path)
    fn.rename(new_path)
    #    print(f"{fn.name} -> ", end="")
    cprint(f"{new_path.name}", "green")
    return 0


def main() -> None:
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = (
        [Path(arg) for arg in args]
        if args
        else get_files(cwd, extensions=[".ttf", ".woff", ".woff2", ".bin", ".otf", ".eot"])
    )
    if not files:
        print("no files found")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(0)
    _ = mpf(process_file, files)


if __name__ == "__main__":
    main()
