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
import csv
import shutil
import sys
from pathlib import Path

from loguru import logger


def find_dist_info_dir(site_packages: Path, pkg_name: str) -> Path:
    candidates = list(site_packages.glob(f"{pkg_name}-*.dist-info"))
    if not candidates:
        norm = pkg_name.replace("-", "_")
        candidates = list(site_packages.glob(f"{norm}-*.dist-info"))
    if not candidates:
        msg = f"Could not find any dist-info directory for package '{pkg_name}' in {site_packages}"
        raise FileNotFoundError(msg)
    if len(candidates) > 1:
        logger.warning("Multiple dist-info directories found for '{}', using: {}", pkg_name, candidates[0])
    return candidates[0]


def copy_package_files(pkg_name: str, site_packages: Path):
    dist_info_dir = find_dist_info_dir(site_packages, pkg_name)
    record_path = dist_info_dir / "RECORD"
    if not record_path.is_file():
        print(f"RECORD file not found: {record_path}")
    dest_root = Path.home() / "tmp" / "1" / pkg_name
    dest_root.mkdir(parents=True, exist_ok=True)
    print("Destination root: {}", dest_root)
    missing_count = copied_count = error_count = 0
    with record_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                if not row:
                    continue
                rel_path = row[0]
                if not rel_path:
                    continue
                src_path = site_packages / rel_path
                if not src_path.exists() and "dist-info" in str(src_path):
                    missing_count += 1
                    continue
                if not src_path.exists() and src_path.suffix != ".pyc":
                    logger.warning("Missing file listed in RECORD: {}", src_path)
                    missing_count += 1
                    continue
                if not src_path.exists():
                    continue
                dest_path = dest_root / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(src_path, dest_path)
                copied_count += 1
            except Exception as e:
                logger.exception("Error while processing RECORD entry {}: {}", row, e)
                error_count += 1
    print("Missing files (warned): {}", missing_count)
    print("Copied: {} | Errors: {}", copied_count, error_count)


def main():
    parser = argparse.ArgumentParser(description="Copy (or move) package files based on RECORD metadata.")
    parser.add_argument("pkg", nargs="?", help="Package name to process")
    parser.add_argument("-a", "--all", action="store_true", help="Process all packages in current directory")
    args = parser.parse_args()
    if not args.pkg and (not args.all):
        parser.error("You must specify a package name or use --all")
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{level}</green>|{message}")
    site_packages = Path.cwd()
    try:
        if args.all:
            dist_infos = list(site_packages.glob("*.dist-info"))
            if not dist_infos:
                logger.error("No .dist-info directories found in {}", site_packages)
                sys.exit(1)
            for dist_dir in dist_infos:
                pkg_name = dist_dir.stem.split("-")[0]
                print("Processing package: {}", pkg_name)
                try:
                    copy_package_files(pkg_name, site_packages)
                except Exception:
                    logger.exception("Failed to copy package {}", pkg_name)
                    continue
        else:
            copy_package_files(args.pkg, site_packages)
    except Exception as e:
        logger.exception("Fatal error: {}", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
