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

import re
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import py7zr
from dh import BIN_EXT, TXT_EXT, get_files

url_pattern = re.compile("https?://[^\\s\"\\']+")
EXT = BIN_EXT
EXT.update(TXT_EXT)


def extract_urls_from_text(content):
    return set(url_pattern.findall(content))


def extract_urls_from_file(filepath):
    urls = set()
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        urls.update(extract_urls_from_text(content))
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
    return urls


def extract_urls_from_tar(filepath):
    urls = set()
    try:
        mode = "r:*"
        with tarfile.open(filepath, mode) as tar:
            for member in tar.getmembers():
                if member.isfile():
                    f = tar.extractfile(member)
                    if f:
                        content = f.read().decode("utf-8", errors="ignore")
                        urls.update(extract_urls_from_text(content))
    except Exception as e:
        print(f"Failed to read tar {filepath}: {e}")
    return urls


def extract_urls_from_zip(filepath):
    urls = set()
    try:
        with zipfile.ZipFile(filepath, "r") as zf:
            for name in zf.namelist():
                try:
                    with zf.open(name) as f:
                        content = f.read().decode("utf-8", errors="ignore")
                        urls.update(extract_urls_from_text(content))
                except:
                    pass
    except Exception as e:
        print(f"Failed to read zip {filepath}: {e}")
    return urls


def extract_urls_from_7z(filepath):
    urls = set()
    try:
        with py7zr.SevenZipFile(filepath, mode="r") as archive:
            all_files = archive.readall()
            for bio in all_files.values():
                try:
                    content = bio.read().decode("utf-8", errors="ignore")
                    urls.update(extract_urls_from_text(content))
                except:
                    pass
    except Exception as e:
        print(f"Failed to read 7z {filepath}: {e}")
    return urls


def extract_urls(filepath):
    path = Path(filepath)
    if path.suffix in EXT:
        return extract_urls_from_file(filepath)
    if path.suffix in {".zip", ".whl"}:
        return extract_urls_from_zip(filepath)
    if path.suffix.startswith(".tar") or path.suffix in {".tar.gz", ".tar.xz", ".tar.zst", ".tar.7z"}:
        return extract_urls_from_tar(filepath)
    if path.suffix == ".7z":
        return extract_urls_from_7z(filepath)
    return set()


if __name__ == "__main__":
    cwd = Path.cwd()
    file_paths = get_files(cwd)
    all_urls = set()
    with ThreadPoolExecutor(8) as executor:
        futures = [executor.submit(extract_urls, fp) for fp in file_paths]
        for future in as_completed(futures):
            all_urls.update(future.result())
    with Path("urls.txt").open("w", encoding="utf-8") as f:
        f.writelines((url + "\n" for url in sorted(all_urls)))
    print(f"Extracted {len(all_urls)} unique URLs to urls.txt")
