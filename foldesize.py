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

import math
import operator
import os
import shutil
from pathlib import Path


def get_all_files_in_root_only(root_path):
    files_info = []
    try:
        for path in root_path.rglob("*"):
            if path.is_file() and (not path.is_symlink()):
                try:
                    size = path.stat().st_size
                    files_info.append({"path": path, "name": path.name, "size": size})
                except OSError as e:
                    print(f"Error accessing {path}: {e}")
    except Exception as e:
        print(f"Error scanning directory: {e}")
    return files_info


def format_size1(size_bytes):
    if size_bytes == 0:
        return "0B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = math.floor(math.log(size_bytes, 1024))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s}{units[i]}"


def calculate_optimal_files_per_folder(total_files, target_folders=None):
    if target_folders:
        return math.ceil(total_files / target_folders)
    if total_files <= 100:
        return 10
    if total_files <= 500:
        return 25
    if total_files <= 1000:
        return 50
    if total_files <= 5000:
        return 100
    return 200


def analyze_size_distribution(files_info):
    if not files_info:
        return {}
    sizes = [f["size"] for f in files_info]
    return {
        "min": min(sizes),
        "max": max(sizes),
        "avg": sum(sizes) / len(sizes),
        "total": sum(sizes),
        "count": len(sizes),
    }


def organize_files_in_root(root_path=".", target_folders=4, max_get_size_mb=None):
    print("=" * 70)
    print("File Organization - Direct to Root Path (No Subdirectories)")
    print("=" * 70)
    root_path = Path(root_path).resolve()
    print(f"\nRoot directory: {root_path}")
    print("Mode: Files will be moved into organized folders in root path")
    print("\n[1/5] Scanning files in root directory...")
    files_info = get_all_files_in_root_only(root_path)
    if not files_info:
        print("No files found in root directory!")
        return
    print("[2/5] Analyzing file size distribution...")
    stats = analyze_size_distribution(files_info)
    print("\nFile Statistics:")
    print(f"  Total files: {stats['count']}")
    print(f"  Total size: {convert_size(stats['total'])}")
    print(f"  Average size: {convert_size(stats['avg'])}")
    print(f"  Size range: {convert_size(stats['min'])} - {convert_size(stats['max'])}")
    print("\n[3/5] Sorting files by size...")
    files_info.sort(key=operator.itemgetter("size"))
    print("[4/5] Calculating optimal folder distribution...")
    if max_get_size_mb:
        max_size_bytes = max_get_size_mb * 1024 * 1024
        folders = []
        current_folder = []
        current_size = 0
        for file_info in files_info:
            if current_size + file_info["size"] > max_size_bytes and current_folder:
                folders.append(current_folder)
                current_folder = []
                current_size = 0
            current_folder.append(file_info)
            current_size += file_info["size"]
        if current_folder:
            folders.append(current_folder)
        files_per_folder = 500
    else:
        files_per_folder = calculate_optimal_files_per_folder(stats["count"], target_folders)
        num_folders = math.ceil(stats["count"] / files_per_folder)
        folders = []
        for i in range(num_folders):
            start_idx = i * files_per_folder
            end_idx = min(start_idx + files_per_folder, stats["count"])
            folders.append(files_info[start_idx:end_idx])
    print("\nOrganization Plan:")
    print(f"  Number of folders to create: {len(folders)}")
    files_per_folder = 500
    if files_per_folder:
        print(f"  Files per folder: ~{files_per_folder}")
    if max_get_size_mb:
        print(f"  Max folder size: {max_get_size_mb} MB")
    print(f"  Folders will be created directly in: {root_path}")
    print("\n[5/5] Creating folders and moving files...")
    moved_count = 0
    error_count = 0
    created_folders = []
    for idx, folder_files in enumerate(folders, 1):
        if not folder_files:
            continue
        min_size = folder_files[0]["size"]
        max_size = folder_files[-1]["size"]
        total_size = sum((f["size"] for f in folder_files))
        folder_name = f"{convert_size(min_size)}-{convert_size(max_size)}"
        folder_name = "".join((c for c in folder_name if c not in '<>:"/\\|?*'))
        folder_path = os.path.join(root_path, folder_name)
        try:
            Path(folder_path).mkdir(exist_ok=True, parents=True)
            created_folders.append(folder_name)
            print(f"\n  Folder {idx}/{len(folders)}: {folder_name}")
            print(f"    Files: {len(folder_files)}")
            print(f"    Size range: {convert_size(min_size)} - {convert_size(max_size)}")
            print(f"    Total size: {convert_size(total_size)}")
            for file_info in folder_files:
                src = file_info["path"]
                dst = os.path.join(folder_path, file_info["name"])
                counter = 1
                base_name, ext = os.path.splitext(file_info["name"])
                while Path(dst).exists():
                    dst = os.path.join(folder_path, f"{base_name}_{counter}{ext}")
                    counter += 1
                try:
                    shutil.move(src, dst)
                    moved_count += 1
                except Exception as e:
                    print(f"      Error moving {file_info['name']}: {e}")
                    error_count += 1
        except Exception as e:
            print(f"  Error creating folder {folder_name}: {e}")
            error_count += len(folder_files)
    print("\n" + "=" * 70)
    print("✓ Organization complete!")
    print(f"  Root directory: {root_path}")
    print(f"  Folders created: {len(created_folders)}")
    print(f"  Files moved: {moved_count}")
    print(f"  Errors: {error_count}")
    print("\nCreated folders:")
    for folder in created_folders:
        print(f"  - {folder}")
    print("=" * 70)


def main():
    ROOT_PATH = "."
    organize_files_in_root(root_path=ROOT_PATH)


if __name__ == "__main__":
    main()
