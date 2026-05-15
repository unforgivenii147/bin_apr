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

import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm

SKIPPED_PATHS = []


def hash_file(path: Path, chunk_size: int = 8192) -> str:
    sha = hashlib.sha256()
    try:
        get_size = path.stat().st_size
        with (
            Path(path).open("rb") as f,
            tqdm(
                total=get_size, unit="B", unit_scale=True, unit_divisor=1024, desc=f"Hashing {path.name}", leave=False
            ) as pbar,
        ):
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha.update(chunk)
                pbar.update(len(chunk))
    except PermissionError:
        SKIPPED_PATHS.append(str(path))
        return None
    except OSError:
        SKIPPED_PATHS.append(str(path))
        return None
    return sha.hexdigest()


def collect_all_files(directory: Path):
    all_files = []
    for root, _dirs, files in os.walk(directory, onerror=lambda e: None):
        for f in files:
            full_path = Path(root) / f
            all_files.append(full_path)
    return all_files


def find_duplicate_files(directory: str):
    directory = Path(directory)
    if not directory.exists():
        msg = f"Directory does not exist: {directory}"
        raise ValueError(msg)
    all_files = collect_all_files(directory)
    duplicates = defaultdict(list)
    print(f"📁 Scanning {len(all_files)} files...\n")
    for file_path in tqdm(all_files, desc="Overall Progress", unit="file"):
        file_hash = hash_file(file_path)
        if file_hash:
            duplicates[file_hash].append(str(file_path))
    return {h: paths for h, paths in duplicates.items() if len(paths) > 1}


def print_duplicates(dups: dict) -> None:
    if not dups:
        print("🎉 No duplicates found!")
        return
    print("\n🔍 Duplicate Files Found:\n")
    for i, (h, paths) in enumerate(dups.items(), start=1):
        print(f"Group {i} (hash={h[:12]}...):")
        for p in paths:
            print(f"   • {p}")
        print("-" * 40)


def export_to_json(dups: dict, output_path="duplicates.json") -> None:
    with Path(output_path).open("w", encoding="utf-8") as f:
        json.dump(dups, f, indent=2)
    print(f"📦 Results exported to {output_path}")


def print_skipped_paths() -> None:
    if not SKIPPED_PATHS:
        return
    print("\n⚠️  Skipped (permission denied):")
    for p in SKIPPED_PATHS:
        print(f"   • {p}")


if __name__ == "__main__":
    folder = input("Enter folder path to scan: ").strip()
    duplicates = find_duplicate_files(folder)
    print_duplicates(duplicates)
    print_skipped_paths()
    if duplicates:
        save = input("Export results to JSON? (y/n): ").lower().strip()
        if save == "y":
            export_to_json(duplicates)
