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

import argparse
import fnmatch
import mmap
from multiprocessing import Pool
from pathlib import Path

from dh import is_binary


def needs_conversion(path: Path) -> bool:
    try:
        with path.open("rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            return mm.find(b"\r\n") != -1
    except Exception:
        return False


def convert_in_place(path: Path) -> None:
    print(f"processing {path.name}")
    with path.open("r+b") as f, mmap.mmap(f.fileno(), 0) as mm:
        data = mm[:]
        new = data.replace(b"\r\n", b"\n")
        if new == data:
            return
        mm.seek(0)
        mm.write(new)
        mm.flush()
        f.truncate(len(new))


def convert_with_temp(path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with (
        path.open("r", encoding="utf-8", errors="ignore", newline="") as src,
        tmp.open("w", encoding="utf-8", newline="") as dst,
    ):
        for line in src:
            dst.write(line.replace("\r\n", "\n"))
    Path(tmp).replace(path)


def safe_convert(path: Path, dry_run: bool = False) -> str:
    if not path.is_file():
        return "SKIP_NOT_FILE"
    if is_binary(path):
        return "SKIP_BINARY"
    if not needs_conversion(path):
        return "SKIP_ALREADY_UNIX"
    if dry_run:
        return "DRY_RUN"
    try:
        convert_in_place(path)
        return "CONVERTED_MMAP"
    except Exception:
        try:
            convert_with_temp(path)
            return "CONVERTED_TEMP"
        except Exception:
            return "ERROR"


def scan_paths(inputs, recursive: bool, excludes) -> list[Path]:
    result = []
    for inp in inputs:
        p = Path(inp)
        if p.is_dir():
            if recursive:
                result.extend(p.rglob("*"))
            else:
                result.extend(p.glob("*"))
        else:
            result.append(p)
    out = []
    for p in result:
        if any((fnmatch.fnmatch(str(p), pat) for pat in excludes)):
            continue
        out.append(p)
    return out


def worker(args):
    path, dry = args
    res = safe_convert(path, dry_run=dry)
    if res == "ERROR":
        print("Failed to convert: %s", path)
    return res


def parse_args():
    parser = argparse.ArgumentParser(description="Fast dos2unix converter with mmap, tqdm")
    parser.add_argument("paths", nargs="*", help="Files or directories.")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--exclude", nargs="*", default=[".git", "__pycache__"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.paths:
        args.paths = ["."]
        args.recursive = True
    files = scan_paths(args.paths, args.recursive, args.exclude)
    tasks = [(p, args.dry_run) for p in files]
    with Pool(4) as pool:
        for _ in pool.imap_unordered(worker, tasks, chunksize=50):
            pass


if __name__ == "__main__":
    main()
