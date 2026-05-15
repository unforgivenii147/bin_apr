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
import sys
from pathlib import Path

from loguru import logger


def find_site_packages() -> Path | None:
    import site

    site_packages_dirs = site.getsitepackages()
    if not site_packages_dirs:
        logger.error("No site-packages directories found")
        return None
    site_packages = Path(site_packages_dirs[0])
    print("Found site-packages directory: %s", site_packages)
    return site_packages


def calculate_file_hash(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    try:
        with Path(filepath).open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        hash_bytes = sha256_hash.digest()
        hash_b64 = base64.urlsafe_b64encode(hash_bytes).decode("ascii").rstrip("=")
        return f"sha256={hash_b64}"
    except Exception as e:
        logger.exception("Error calculating hash for %s: %s", filepath, e)
        return ""


def gsz(filepath: Path) -> int:
    try:
        return filepath.stat().st_size
    except Exception as e:
        logger.exception("Error getting size for %s: %s", filepath, e)
        return 0


def parse_record_line(line: str) -> tuple[str, str, str]:
    parts = line.strip().split(",")
    if len(parts) == 3:
        return (parts[0], parts[1], parts[2])
    if len(parts) == 2:
        return (parts[0], parts[1], "")
    return (parts[0], "", "")


def should_include_file(filepath: Path) -> bool:
    if filepath.suffix == ".pyc" or filepath.name.endswith(".pyc"):
        return False
    if filepath.name == "direct_url.json":
        return False
    if filepath.name == "INSTALLER":
        return False
    return filepath.name != "RECORD"


def update_record_file(record_path: Path, dist_info_dir) -> bool:
    print("Processing %s", record_path)
    if not record_path.exists():
        logger.error("RECORD file not found: %s", record_path)
        return False
    try:
        with Path(record_path).open(encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        logger.exception("Error reading %s: %s", record_path, e)
        return False
    new_lines = []
    missing_files = []
    for ln in lines:
        line = ln.strip()
        if not line:
            continue
        relative_path, _old_hash, _old_size = parse_record_line(line)
        if relative_path == "RECORD":
            continue
        full_path = dist_info_dir.parent / relative_path
        if not should_include_file(full_path):
            logger.debug("Skipping %s (excluded file type)", relative_path)
            continue
        if not full_path.exists():
            missing_files.append(relative_path)
            logger.warning("Missing file: %s", relative_path)
            continue
        new_hash = calculate_file_hash(full_path)
        new_size = gsz(full_path)
        if new_hash:
            new_lines.append(f"{relative_path},{new_hash},{new_size}")
        else:
            logger.warning("Failed to calculate hash for %s, keeping original", relative_path)
            new_lines.append(line)
    record_relative = str(record_path.relative_to(dist_info_dir.parent))
    new_lines.append(f"{record_relative},,")
    if missing_files:
        print(f"Found {len(missing_files)} missing files in {dist_info_dir.name}:")
        for missing in missing_files:
            print("  - %s", missing)
    try:
        Path(record_path).write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print("Successfully updated %s", record_path)
        update_record_self_hash(record_path, dist_info_dir)
        return True
    except Exception as e:
        logger.exception("Error writing %s: %s", record_path, e)
        return False


def update_record_self_hash(record_path: Path):
    try:
        with Path(record_path).open(encoding="utf-8") as f:
            lines = f.readlines()
        record_hash = calculate_file_hash(record_path)
        record_size = gsz(record_path)
        if lines:
            last_line = lines[-1].strip()
            parts = last_line.split(",")
            if len(parts) >= 1:
                record_relative = parts[0]
                lines[-1] = f"{record_relative},{record_hash},{record_size}\n"
        with Path(record_path).open("w", encoding="utf-8") as f:
            f.writelines(lines)
        logger.debug("Updated self-hash for %s", record_path)
    except Exception as e:
        logger.exception("Error updating self-hash for %s: %s", record_path, e)


def scan_and_update():
    site_packages = find_site_packages()
    if not site_packages:
        return
    dist_info_dirs = list(site_packages.glob("*.dist-info"))
    if not dist_info_dirs:
        logger.warning("No .dist-info directories found in %s", site_packages)
        return
    print(f"Found {len(dist_info_dirs)} distribution info directories")
    updated_count = 0
    failed_count = 0
    for dist_info_dir in dist_info_dirs:
        record_path = dist_info_dir / "RECORD"
        if update_record_file(record_path, dist_info_dir):
            updated_count += 1
        else:
            failed_count += 1
    print("Summary: %s RECORD files updated, %s failed", updated_count, failed_count)


def main():
    print("Starting site-packages RECORD file updater")
    try:
        scan_and_update()
    except KeyboardInterrupt:
        print("Script interrupted by user")
        sys.exit(1)
    print("Script completed successfully")


if __name__ == "__main__":
    main()
