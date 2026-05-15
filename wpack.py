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

import asyncio
import multiprocessing
import sys
import zipfile
from pathlib import Path

from wheel.archive import wheel_load
from wheel.wheelfile import WheelFile

UNPACKED_WHEELS_SOURCE_DIR = Path.cwd()
WHEELS_OUTPUT_DIR = None


def find_dist_info_dir(pkg_dir: Path) -> Path | None:
    candidates = [p for p in pkg_dir.iterdir() if p.is_dir() and p.name.endswith(".dist-info")]
    if not candidates:
        return None
    if len(candidates) > 1:
        print(
            f"Warning: Multiple .dist-info dirs found in {pkg_dir}, using the first: {candidates[0].name}",
            file=sys.stderr,
        )
    return candidates[0]


def create_wheel_for_dir_sync(pkg_dir: Path, dest_dir: Path | None = None) -> tuple[str, bool]:
    dist_info = find_dist_info_dir(pkg_dir)
    if dist_info is None:
        print(f"Skipping {pkg_dir}: no *.dist-info dir found.")
        return (pkg_dir.name, False)
    try:
        metadata = wheel_load(dist_info)
        wheel_filename = metadata.WheelFilename
    except Exception as e:
        print(f"Error loading metadata from {dist_info}: {e}")
        return (pkg_dir.name, False)
    output_path = dest_dir / wheel_filename if dest_dir else Path(wheel_filename)
    if dest_dir:
        dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        with WheelFile(str(output_path), "w", compression=zipfile.ZIP_DEFLATED) as wf:
            for item in pkg_dir.rglob("*"):
                if item.is_file():
                    arcname = item.relative_to(pkg_dir).as_posix()
                    wf.write_to(str(item), arcname)
        return (wheel_filename, True)
    except Exception as e:
        print(f"Error creating wheel for {pkg_dir}: {e}")
        if output_path.exists():
            output_path.unlink()
        return (wheel_filename, False)


async def process_package_async(pkg_dir: Path, dest_dir: Path | None, task_queue: asyncio.Queue):
    loop = asyncio.get_running_loop()
    wheel_filename, success = await loop.run_in_executor(None, create_wheel_for_dir_sync, pkg_dir, dest_dir)
    await task_queue.put_nowait((wheel_filename, success))


async def main_async():
    if WHEELS_OUTPUT_DIR:
        WHEELS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Output directory for wheels: {WHEELS_OUTPUT_DIR}")
    tasks = []
    task_queue = asyncio.Queue()
    dirs_to_process = []
    for entry in UNPACKED_WHEELS_SOURCE_DIR.iterdir():
        if entry.is_dir() and (not entry.name.endswith(".dist-info")):
            dist_info = find_dist_info_dir(entry)
            if dist_info:
                dirs_to_process.append(entry)
    if not dirs_to_process:
        print("No valid unpacked wheel directories found.")
        return
    print(f"Found {len(dirs_to_process)} directories to process.")
    for pkg_dir in dirs_to_process:
        task = asyncio.create_task(process_package_async(pkg_dir, WHEELS_OUTPUT_DIR, task_queue))
        tasks.append(task)
    await asyncio.gather(*tasks)
    successful_wheels = []
    failed_wheels = []
    while not task_queue.empty():
        wheel_filename, success = await task_queue.get()
        if success:
            successful_wheels.append(wheel_filename)
        else:
            failed_wheels.append(wheel_filename)
    print("\n--- Wheel Packing Summary ---")
    print(f"Successfully created wheels: {len(successful_wheels)}")
    if successful_wheels:
        print("  - " + "\n  - ".join(successful_wheels))
    if failed_wheels:
        print(f"Failed to create wheels: {len(failed_wheels)}")
        print("  - " + "\n  - ".join(failed_wheels))
    print("\nDone.")


def main_multiprocessing():
    if WHEELS_OUTPUT_DIR:
        WHEELS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Output directory for wheels: {WHEELS_OUTPUT_DIR}")
    dirs_to_process = []
    for entry in UNPACKED_WHEELS_SOURCE_DIR.iterdir():
        whl = Path(str(entry.name) + ".whl")
        if whl.exists():
            continue
        if entry.is_dir() and (not entry.name.endswith(".dist-info")):
            dist_info = find_dist_info_dir(entry)
            if dist_info:
                dirs_to_process.append(entry)
    if not dirs_to_process:
        print("No valid unpacked wheel directories found.")
        return
    print(f"Found {len(dirs_to_process)} directories to process.")
    num_processes = multiprocessing.cpu_count()
    print(f"Using {num_processes} worker processes.")
    results = []
    with multiprocessing.Pool(processes=num_processes) as pool:
        worker_args = [(pkg_dir, WHEELS_OUTPUT_DIR) for pkg_dir in dirs_to_process]
        results = pool.starmap(create_wheel_for_dir_sync, worker_args)
    successful_wheels = [res[0] for res in results if res[1]]
    failed_wheels = [res[0] for res in results if not res[1]]
    print("\n--- Wheel Packing Summary ---")
    print(f"Successfully created wheels: {len(successful_wheels)}")
    if successful_wheels:
        print("  - " + "\n  - ".join(successful_wheels))
    if failed_wheels:
        print(f"Failed to create wheels: {len(failed_wheels)}")
        print("  - " + "\n  - ".join(failed_wheels))
    print("\nDone.")


if __name__ == "__main__":
    try:
        pass
    except ImportError:
        print("Error: The 'wheel' library is not installed.")
        print("Please install it using: pip install wheel")
        sys.exit(1)
    main_multiprocessing()
