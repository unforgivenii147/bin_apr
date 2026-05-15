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

from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


CHUNK_SIZE = 524288
MAX_BYTE_INDEX = 19


class QuickXorHash:
    def __init__(self) -> None:
        self._hash = [0] * 20
        self._length = 0

    def update(self, data: bytes):
        for b in data:
            shift = self._length % 160
            byte_index = shift // 8
            bit_index = shift % 8
            self._hash[byte_index] ^= b << bit_index & 255
            if bit_index > 0 and byte_index < MAX_BYTE_INDEX:
                self._hash[byte_index + 1] ^= b >> 8 - bit_index & 255
            self._length += 1

    def digest(self):
        length_bytes = self._length.to_bytes(8, "little")
        for i in range(8):
            self._hash[20 - 8 + i] ^= length_bytes[i]
        return bytes(self._hash)

    def hexdigest(self):
        return b64encode(self.digest()).decode("ascii")


def calculate_xorhash(path: Path) -> str:
    q = QuickXorHash()
    try:
        with path.open("rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                q.update(chunk)
        return (q.hexdigest(), path)
    except Exception as e:
        print(f"Error hashing file {path}: {e}")
        return (None, path)


def find_dups_optimized(root: Path):
    file_hashes = {}
    paths_to_process = []
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        try:
            if not path.is_symlink() and path.is_file():
                paths_to_process.append(path)
        except OSError as e:
            print(f"Error accessing path {path}: {e}")
            continue
    if not paths_to_process:
        return {}
    files_by_size = {}
    for path in paths_to_process:
        try:
            size = path.stat().st_size
            files_by_size.setdefault(size, []).append(path)
        except OSError as e:
            print(f"Error getting size for {path}: {e}")
            continue
    paths_to_hash = []
    for paths in files_by_size.values():
        if len(paths) > 1:
            paths_to_hash.extend(paths)
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_path = {executor.submit(calculate_xorhash, path): path for path in paths_to_hash}
        for future in as_completed(future_to_path):
            hash_result, path = future.result()
            if hash_result is not None:
                file_hashes.setdefault(hash_result, []).append(path)
    return {h: paths for h, paths in file_hashes.items() if len(paths) > 1}


if __name__ == "__main__":
    cwd = Path.cwd()
    print(f"Scanning directory: {cwd}")
    dupes = find_dups_optimized(cwd)
    if not dupes:
        print("No duplicate files found.")
    else:
        print(f"Found {len(dupes)} group(s) of duplicate files:")
        for h, paths in dupes.items():
            print(f"Duplicate group ({h}):")
            for p in paths:
                print("  ", p)
