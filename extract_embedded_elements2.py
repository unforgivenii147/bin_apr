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
import mimetypes
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

cwd = Path.cwd()
INPUT_DIR = cwd
OUTPUT_DIR = cwd / "output"
ASSETS_DIR = cwd / "output" / "assets"
DOWNLOAD_REMOTE = False
TIMEOUT = 10
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def save_asset(content: bytes, mime_type: str, file_hint="asset"):
    ext = mimetypes.guess_extension(mime_type) or ""
    counter = 0
    while True:
        fname = f"{file_hint}_{counter}{ext}"
        fpath = ASSETS_DIR / fname
        if not fpath.exists():
            break
        counter += 1
    fpath.write_bytes(content)
    return fpath


def extract_base64_data(data_url, file_hint="asset"):
    m = re.match("data:(.*?);base64,(.*)", data_url, re.DOTALL)
    if not m:
        return None
    mime_type, encoded = m.groups()
    content = base64.b64decode(encoded)
    return save_asset(content, mime_type, file_hint)


def download_external_url(url, file_hint="remote"):
    try:
        print("Downloading:", url)
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        mime = r.headers.get("Content-Type", "application/octet-stream")
        return save_asset(r.content, mime.split(";")[0], file_hint)
    except Exception:
        return None


def process_file(path: Path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    file_prefix = path.stem
    for i, style_tag in enumerate(soup.find_all("style")):
        if not style_tag.string:
            continue
        css = style_tag.string
        fpath = save_asset(css.encode("utf-8"), "text/css", f"{file_prefix}_style{i}")
        style_tag.replace_with(f'<link rel="stylesheet" href="{fpath.relative_to(OUTPUT_DIR)}">')
    for i, script in enumerate(soup.find_all("script")):
        if script.get("src"):
            src = script.get("src")
            if src.startswith("http") and DOWNLOAD_REMOTE:
                fpath = download_external_url(src, f"{file_prefix}_script_remote")
                if fpath:
                    script["src"] = str(fpath.relative_to(OUTPUT_DIR))
            continue
        js = script.string or ""
        fpath = save_asset(js.encode("utf-8"), "application/javascript", f"{file_prefix}_script{i}")
        script.replace_with(f'<script src="{fpath.relative_to(OUTPUT_DIR)}"></script>')
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith("data:"):
            fpath = extract_base64_data(src, f"{file_prefix}_img")
            if fpath:
                img["src"] = str(fpath.relative_to(OUTPUT_DIR))
        elif src.startswith("http") and DOWNLOAD_REMOTE:
            fpath = download_external_url(src, f"{file_prefix}_img_remote")
            if fpath:
                img["src"] = str(fpath.relative_to(OUTPUT_DIR))
    bg_re = re.compile('url\\("(data:.*?)"\\)')
    for tag in soup.find_all(style=True):
        style = tag["style"]
        m = bg_re.search(style)
        if m:
            data_url = m.group(1)
            fpath = extract_base64_data(data_url, f"{file_prefix}_bg")
            if fpath:
                tag["style"] = style.replace(data_url, str(fpath.relative_to(OUTPUT_DIR)))
    for i, svg in enumerate(soup.find_all("svg")):
        svg_str = str(svg)
        fpath = save_asset(svg_str.encode("utf-8"), "image/svg+xml", f"{file_prefix}_svg{i}")
        new_tag = soup.new_tag("img")
        new_tag["src"] = str(fpath.relative_to(OUTPUT_DIR))
        svg.replace_with(new_tag)
    for style in soup.find_all("style"):
        if not style.string:
            continue
        new_css = style.string
        fonts = re.findall('url\\("(data:font\\/.+?)"\\)', new_css)
        for f in fonts:
            fpath = extract_base64_data(f, f"{file_prefix}_font")
            if fpath:
                new_css = new_css.replace(f, str(fpath.relative_to(OUTPUT_DIR)))
        style.string.replace_with(new_css)
    for link in soup.find_all("link", href=True):
        href = link["href"]
        if href.startswith("http") and DOWNLOAD_REMOTE:
            fpath = download_external_url(href, f"{file_prefix}_css_remote")
            if fpath:
                link["href"] = str(fpath)
    output_html_path = OUTPUT_DIR / path.relative_to(INPUT_DIR)
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    output_html_path.write_text(str(soup), encoding="utf-8")
    print("Processed:", path)


if __name__ == "__main__":
    for path in cwd.rglob("*"):
        if path.suffix.lower() in {".html", ".htm"} and "output" not in path.parts:
            process_file(path)
    print("\nAll done — extracted assets saved to ./output/")
