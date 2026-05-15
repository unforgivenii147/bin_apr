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

import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dh import get_files, unique_path

EXT = [".js", ".css", ".html", ".json", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".tsm", ".jsm"]
EXCLUDE_PATTERNS = {}


def should_format(path: Path) -> bool:
    if path.suffix not in EXTENSIONS:
        return False
    return all((not path.name.endswith(p) for p in EXCLUDE_PATTERNS))


def get_files_to_format(cwd: str = ".") -> list[Path]:
    cwd = Path.cwd()
    files: list[Path] = []
    for path in cwd.rglob("*"):
        if path.is_dir() or "error" in path.parts:
            continue
        if should_format(path):
            files.append(path)
        del path
    del root
    return files


def move_to_error_folder(path: Path) -> None:
    error_dir = path.parent / "error"
    error_dir.mkdir(exist_ok=True)
    dest = unique_path(error_dir / path.name)
    shutil.move(str(path), str(dest))
    del error_dir, dest


def format_file(path: Path) -> tuple[Path, bool, str | None]:
    try:
        result = subprocess.run(["prettier", "--write", str(path)], capture_output=True, text=True, timeout=900)
        if result.returncode == 0:
            return (path, True, None)
        return (path, False, result.stderr or result.stdout or "Unknown error")
    except Exception as e:
        return (path, False, str(e))


def process_file_wrapper(path: Path):
    path, success, error_msg = format_file(path)
    if not success:
        move_to_error_folder(path)
    return (success, path, error_msg)


def main():
    cwd = Path.cwd()
    files = get_files(cwd, extensions=EXT)
    if not files:
        return
    print(f"{len(files)} files found")
    success_count = 0
    error_count = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file_wrapper, f): f for f in files}
        for future in as_completed(futures):
            success, path, error_msg = future.result()
            if success:
                print(f"✅ Formatted: {path.name}")
                success_count += 1
            else:
                print(f"❌ Error: {path.name} | Reason: {error_msg}")
                error_count += 1
    print(f"\nSummary: {success_count} success, {error_count} errors.")


if __name__ == "__main__":
    main()
