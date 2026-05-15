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

import os
import re
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import brotli
import chardet
from loguru import logger

TARGET_EXTENSIONS = {".tar.gz", ".pdf", ".zip", ".css", ".js", ".tar.xz", ".7z", ".whl", ".html"}
COMPRESSED_ARCHIVES = {".tar.xz", ".tar.gz", ".tar.zst", ".7z", ".br", ".zip", ".whl"}
GITHUB_REPO_REGEX = re.compile("https?://(?:www\\.)?github\\.com/[a-zA-Z0-9\\-]+/[a-zA-Z0-9\\-]+")
URL_REGEX = re.compile("(http|ftp|https)://([\\w_-]+(?:(?:\\.[\\w_-]+)+))([\\w.,@?^=%&:/~+#-]*[\\w@?^=%&/~+#-])?")
MAX_WORKERS = 4
BINARY_CHECK_THRESHOLD = 0.7


def extract_links_from_text(text, file_path):
    urls = URL_REGEX.findall(text)
    github_urls = GITHUB_REPO_REGEX.findall(text)
    return (urls, github_urls)


def is_likely_binary(file_path, chunk_size=1024):
    try:
        with Path(file_path).open("rb") as f:
            chunk = f.read(chunk_size)
            if not chunk:
                return False
            result = chardet.detect(chunk)
            return bool(
                (result["encoding"] is None or result["confidence"] < BINARY_CHECK_THRESHOLD)
                and any(
                    (
                        not (32 <= ord(c) <= 126 or c in "\n\r\t")
                        for c in chunk.decode(result["encoding"] or "latin-1", errors="ignore")
                    )
                )
            )
    except Exception as e:
        logger.warning(f"Could not reliably determine if {file_path} is binary: {e}")
        return True


def read_file_with_encodings(file_path):
    encodings_to_try = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
    for encoding in encodings_to_try:
        try:
            content = Path(file_path).read_text(encoding=encoding)
            logger.debug(f"Successfully read {file_path} with {encoding}")
            return (content, None)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.warning(f"Error reading {file_path} with {encoding}: {e}")
            continue
    try:
        raw_data = Path(file_path).read_bytes()
        result = chardet.detect(raw_data)
        detected_encoding = result["encoding"]
        if detected_encoding:
            try:
                content = raw_data.decode(detected_encoding)
                logger.debug(f"Successfully read {file_path} with detected encoding {detected_encoding}")
                return (content, detected_encoding)
            except Exception as e:
                logger.warning(f"Error decoding {file_path} with detected encoding {detected_encoding}: {e}")
    except Exception as e:
        logger.error(f"Failed to read or detect encoding for {file_path}: {e}")
    return (None, None)


def process_file(file_path):
    local_urls = []
    github_urls = []
    file_path = Path(file_path)
    file_extension = file_path.suffix.lower()
    if not file_path.is_file():
        return ([], [])
    try:
        if file_extension in TARGET_EXTENSIONS:
            if file_extension == ".pdf":
                content, _ = read_file_with_encodings(file_path)
                if content:
                    urls, gh_urls = extract_links_from_text(content, file_path)
                    local_urls.extend(urls)
                    github_urls.extend(gh_urls)
                    logger.debug(f"Extracted from PDF: {file_path}")
                else:
                    logger.warning(f"Could not decode PDF content for {file_path}")
            elif file_extension in {".tar.gz", ".tar.xz", ".tar.zst", ".zip", ".7z", ".whl"}:
                try:
                    if file_extension in {".tar.gz", ".tar.xz"}:
                        with tarfile.open(file_path, "r:*") as tar:
                            for member in tar.getmembers():
                                if member.isfile():
                                    try:
                                        f = tar.extractfile(member)
                                        if f:
                                            member_content_bytes = f.read()
                                            member_content_str, _ = read_file_with_encodings(file_path)
                                            if member_content_str:
                                                urls, gh_urls = extract_links_from_text(
                                                    member_content_str, f"{file_path}/{member.name}"
                                                )
                                                local_urls.extend(urls)
                                                github_urls.extend(gh_urls)
                                    except Exception as e:
                                        logger.warning(f"Error processing member {member.name} in {file_path}: {e}")
                        logger.debug(f"Extracted from Tar archive: {file_path}")
                    elif file_extension in {".zip", ".whl"}:
                        with zipfile.ZipFile(file_path, "r") as zip_ref:
                            for file_info in zip_ref.infolist():
                                if not file_info.is_dir():
                                    with zip_ref.open(file_info) as f:
                                        member_content_bytes = f.read()
                                        member_content_str, _ = read_file_with_encodings(file_path)
                                        if member_content_str:
                                            urls, gh_urls = extract_links_from_text(
                                                member_content_str, f"{file_path}/{file_info.filename}"
                                            )
                                            local_urls.extend(urls)
                                            github_urls.extend(gh_urls)
                        logger.debug(f"Extracted from ZIP archive: {file_path}")
                    elif file_extension == ".7z":
                        logger.warning(
                            f"7z extraction requires external library like 'py7zr'. Treating as binary for now: {file_path}"
                        )
                        if is_likely_binary(file_path):
                            content, _ = read_file_with_encodings(file_path)
                            if content:
                                urls, gh_urls = extract_links_from_text(content, file_path)
                                local_urls.extend(urls)
                                github_urls.extend(gh_urls)
                        else:
                            logger.warning(f"File {file_path} identified as text, but couldn't extract from 7z.")
                except (
                    tarfile.TarError,
                    zipfile.BadZipFile,
                    zstandard.ZstdError,
                    brotli.Error,
                    EOFError,
                    ValueError,
                ) as e:
                    logger.warning(f"Could not open/read archive {file_path}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error processing archive {file_path}: {e}")
            elif file_extension in {".css", ".js", ".html"}:
                content, _ = read_file_with_encodings(file_path)
                if content:
                    urls, gh_urls = extract_links_from_text(content, file_path)
                    local_urls.extend(urls)
                    github_urls.extend(gh_urls)
                    logger.debug(f"Extracted from text file: {file_path}")
                else:
                    logger.warning(f"Could not read text file {file_path} with any encoding.")
        elif file_extension not in COMPRESSED_ARCHIVES:
            content, _encoding = read_file_with_encodings(file_path)
            if content:
                urls, gh_urls = extract_links_from_text(content, file_path)
                local_urls.extend(urls)
                github_urls.extend(gh_urls)
                logger.debug(f"Extracted from generic text file: {file_path}")
        if (
            is_likely_binary(file_path)
            and file_extension not in TARGET_EXTENSIONS
            and (file_extension not in COMPRESSED_ARCHIVES)
        ):
            content, _ = read_file_with_encodings(file_path)
            if content:
                urls, gh_urls = extract_links_from_text(content, file_path)
                local_urls.extend(urls)
                github_urls.extend(gh_urls)
                logger.debug(f"Extracted potential URLs from binary-like file: {file_path}")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
    return (list(set(local_urls)), list(set(github_urls)))


def find_files_recursively(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)


if __name__ == "__main__":
    current_directory = "."
    all_extracted_urls = []
    all_github_urls = []
    print(f"Starting URL extraction in directory: {Path(current_directory).resolve()}")
    files_to_process = list(find_files_recursively(current_directory))
    print(f"Found {len(files_to_process)} files to process.")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, file_path): file_path for file_path in files_to_process}
        for future in futures:
            file_path = futures[future]
            try:
                urls, gh_urls = future.result()
                all_extracted_urls.extend(urls)
                all_github_urls.extend(gh_urls)
            except Exception as e:
                logger.error(f"Error processing result for {file_path}: {e}")
    unique_urls = sorted(set(all_extracted_urls))
    unique_github_urls = sorted(set(all_github_urls))
    print("\n--- Extracted URLs ---")
    if unique_urls:
        with Path("urls").open("a", encoding="utf-8") as fo:
            for url in unique_urls:
                print(url)
                fo.write(f"{url}\n")
    else:
        print("No URLs found.")
    print("\n--- Extracted GitHub URLs ---")
    if unique_github_urls:
        with Path("giturls").open("a", encoding="utf-8") as fg:
            for url in unique_github_urls:
                fg.write(f"{url}\n")
                print(url)
    else:
        print("No GitHub URLs found.")
    print(
        f"Extraction complete. Found {len(unique_urls)} unique URLs and {len(unique_github_urls)} unique GitHub URLs."
    )
