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

import base64
import os
import re
import sys
from pathlib import Path

import requests
from loguru import logger

STATIC_DIR = "/sdcard/_static"


def get_file_extension(url):
    return os.path.splitext(url)[1].lower()


def is_font_url(url):
    extensions = [".woff", ".woff2", ".ttf", ".eot", ".svg"]
    return any((url.lower().endswith(ext) for ext in extensions))


def find_local_font(font_filename):
    if not Path(STATIC_DIR).is_dir():
        return None
    for root, _, files in os.walk(STATIC_DIR):
        if font_filename in files:
            return os.path.join(root, font_filename)
    return None


def get_local_font_base64(local_path):
    try:
        content = Path(local_path).read_bytes()
        ext = get_file_extension(local_path)
        content_type = ""
        if ext == ".eot":
            content_type = "application/vnd.ms-fontobject"
        elif ext == ".ttf":
            content_type = "application/font-sfnt"
        elif ext == ".woff":
            content_type = "application/font-woff"
        elif ext == ".woff2":
            content_type = "font/woff2"
        elif ext == ".svg":
            content_type = "image/svg+xml"
        else:
            return None
        encoded_string = base64.b64encode(content).decode("utf-8")
        return f"data:{content_type};charset=utf-8;base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Error: Local font file not found at {local_path}")
        return None
    except Exception as e:
        print(f"An error occurred reading local font {local_path}: {e}")
        return None


def get_remote_font_base64(url):
    try:
        response = requests.get(url, timeout=15, stream=True)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").split(";")[0]
        if not content_type.lower().startswith("font") and "svg" not in content_type.lower():
            print(f"Warning: Content-Type '{content_type}' for {url} doesn't look like a font. Proceeding anyway.")
        ext = get_file_extension(url)
        if ext == ".eot":
            content_type = "application/vnd.ms-fontobject"
        elif ext == ".ttf":
            content_type = "application/font-sfnt"
        elif ext == ".woff":
            content_type = "application/font-woff"
        elif ext == ".woff2":
            content_type = "font/woff2"
        elif ext == ".svg":
            content_type = "image/svg+xml"
        else:
            return None
        encoded_string = base64.b64encode(response.content).decode("utf-8")
        return f"data:{content_type};charset=utf-8;base64,{encoded_string}"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching remote font {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred for remote font {url}: {e}")
        return None


def url_to_base64(url, base_css_path):
    cleaned_url = url.strip("'\"")
    font_filename = Path(cleaned_url).name
    logger.debug(f"looking for {font_filename} in {STATIC_DIR}")
    local_path = find_local_font(font_filename)
    if local_path:
        print(f"Found local font: {font_filename} at {local_path}")
        return get_local_font_base64(local_path)
    full_url = cleaned_url
    if not cleaned_url.startswith(("http://", "https://", "//")):
        base_dir = Path(Path(base_css_path).resolve()).parent
        full_url = os.path.normpath(Path(base_dir) / cleaned_url)
        if not full_url.startswith(("http://", "https://", "//")):
            full_url = f"file:///{full_url}"
    print(f"Attempting to fetch remote font: {full_url}")
    return get_remote_font_base64(full_url)


def make_css_standalone(input_css_path, output_css_path):
    input_css_path = Path(input_css_path).resolve()
    try:
        content = Path(input_css_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: Input CSS file not found at {input_css_path}")
        return
    except Exception as e:
        print(f"Error reading input CSS file {input_css_path}: {e}")
        return
    import_pattern = re.compile("@import\\s+(?:url\\()?([\"\\'])(.*?)\\1\\)?;", re.IGNORECASE)
    font_url_pattern = re.compile("url\\(([\"\\']?)([^)\"\\'\\s]+?)\\1?\\)", re.IGNORECASE)
    processed_content = content
    import_urls_to_process = []
    for match in import_pattern.finditer(content):
        import_url = match.group(2)
        import_urls_to_process.append(import_url)
        processed_content = processed_content.replace(match.group(0), "", 1)
    processed_imports = set()
    queue = import_urls_to_process.copy()
    while queue:
        current_import_url = queue.pop(0)
        normalized_import_url = os.path.normpath(current_import_url)
        if normalized_import_url in processed_imports:
            continue
        processed_imports.add(normalized_import_url)
        print(f"Processing imported CSS: {current_import_url}")
        try:
            if not current_import_url.startswith(("http://", "https://", "//")):
                base_dir = Path(Path(input_css_path).resolve()).parent
                fetch_url = os.path.normpath(Path(base_dir) / current_import_url)
                if not fetch_url.startswith(("http://", "https://", "//")):
                    if Path(fetch_url).exists():
                        imported_css = Path(fetch_url).read_text(encoding="utf-8")
                        import_source_ref = fetch_url
                    else:
                        print(f"Warning: Local import file not found: {fetch_url}. Skipping.")
                        continue
                else:
                    response = requests.get(current_import_url, timeout=15)
                    response.raise_for_status()
                    imported_css = response.text
                    import_source_ref = current_import_url
            else:
                response = requests.get(current_import_url, timeout=15)
                response.raise_for_status()
                imported_css = response.text
                import_source_ref = current_import_url
            for sub_match in import_pattern.finditer(imported_css):
                sub_import_url = sub_match.group(2)
                if os.path.normpath(sub_import_url) not in processed_imports:
                    queue.append(sub_import_url)
                imported_css = imported_css.replace(sub_match.group(0), "", 1)
            processed_content += f"\n/* Imported from: {import_source_ref} */\n{imported_css}\n"
        except FileNotFoundError:
            print(f"Could not import local file {current_import_url} (resolved to {fetch_url}): File not found.")
        except requests.exceptions.RequestException as e:
            print(f"Could not import remote CSS from {current_import_url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing import {current_import_url}: {e}")

    def replace_font_urls_in_content(match):
        url_part = match.group(2)
        quote_style = match.group(1)
        base64_data = url_to_base64(url_part, input_css_path)
        if base64_data:
            if quote_style:
                return f"url({quote_style}{base64_data}{quote_style})"
            return f'url("{base64_data}")'
        print(f"Failed to process font URL: {url_part}. Keeping original.")
        return match.group(0)

    processed_content = font_url_pattern.sub(replace_font_urls_in_content, processed_content)
    try:
        output_dir = Path(output_css_path).parent
        if output_dir:
            Path(output_dir).mkdir(exist_ok=True, parents=True)
        Path(output_css_path).write_text(processed_content, encoding="utf-8")
        print(f"Standalone CSS file created at: {output_css_path}")
    except Exception as e:
        print(f"Error writing output CSS file {output_css_path}: {e}")


if __name__ == "__main__":
    infile = Path(sys.argv[1])
    outfile = infile.with_stem(infile.stem + "_standalone")
    make_css_standalone(infile, outfile)
