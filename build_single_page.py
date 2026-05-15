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
import hashlib
import mimetypes
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

cwd = Path.cwd()
OUTPUT_DIR = cwd / "output"
ASSETS_DIR = cwd / "output" / "assets"
DOWNLOAD_REMOTE = True
TIMEOUT = 10
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
if not ASSETS_DIR.exists():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
HASH_MAP = {}


def sha256(data: bytes):
    return hashlib.sha256(data).hexdigest()


def save_hashed_asset(content: bytes, mime_type: str):
    digest = sha256(content)
    if digest in HASH_MAP:
        return HASH_MAP[digest]
    ext = mimetypes.guess_extension(mime_type) or ""
    fname = f"{digest}{ext}"
    fpath = ASSETS_DIR / fname
    fpath.write_bytes(content)
    HASH_MAP[digest] = fpath
    return fpath


def extract_base64(data_url):
    m = re.match("data:(.*?);base64,(.*)", data_url, re.DOTALL)
    if not m:
        return None
    mime_type, encoded = m.groups()
    content = base64.b64decode(encoded)
    return save_hashed_asset(content, mime_type)


def download_external(url):
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        mime = r.headers.get("Content-Type", "application/octet-stream")
        return save_hashed_asset(r.content, mime.split(";")[0])
    except Exception:
        return None


processed_html_files = []


def process_html(path: Path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    processed_html_files.append(soup)
    file_prefix = path.stem
    for style in soup.find_all("style"):
        if not style.string:
            continue
        css = style.string.encode("utf-8")
        fpath = save_hashed_asset(css, "text/css")
        style.replace_with(f'<link rel="stylesheet" href="{fpath.relative_to(OUTPUT_DIR)}">')
    for script in soup.find_all("script"):
        if script.get("src"):
            src = script["src"]
            if src.startswith("http") and DOWNLOAD_REMOTE:
                fpath = download_external(src)
                if fpath:
                    script["src"] = str(fpath.relative_to(OUTPUT_DIR))
            continue
        js = (script.string or "").encode("utf-8")
        fpath = save_hashed_asset(js, "application/javascript")
        script.replace_with(f'<script src="{fpath.relative_to(OUTPUT_DIR)}"></script>')
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith("data:"):
            fpath = extract_base64(src)
            if fpath:
                img["src"] = str(fpath.relative_to(OUTPUT_DIR))
    bg_re = re.compile('url\\("(data:.*?)"\\)')
    for tag in soup.find_all(style=True):
        m = bg_re.search(tag["style"])
        if m:
            data_url = m.group(1)
            fpath = extract_base64(data_url)
            if fpath:
                tag["style"] = tag["style"].replace(data_url, str(fpath.relative_to(OUTPUT_DIR)))
    for svg in soup.find_all("svg"):
        svg_bytes = str(svg).encode("utf-8")
        fpath = save_hashed_asset(svg_bytes, "image/svg+xml")
        new_tag = soup.new_tag("img")
        new_tag["src"] = str(fpath.relative_to(OUTPUT_DIR))
        svg.replace_with(new_tag)
    for link in soup.find_all("link", href=True):
        href = link["href"]
        if href.startswith("http") and DOWNLOAD_REMOTE:
            print(href)
    out_path = OUTPUT_DIR / path.relative_to(cwd)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(str(soup), encoding="utf-8")
    print("Processed:", path)


def build_single_page():
    merged = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")
    head = merged.head
    body = merged.body
    for soup in processed_html_files:
        if soup.body:
            for el in soup.body.contents:
                body.append(el)
    for asset_file in ASSETS_DIR.iterdir():
        mime = mimetypes.guess_type(asset_file.name)[0] or "application/octet-stream"
        data = asset_file.read_bytes()
        encoded = base64.b64encode(data).decode()
        data_url = f"data:{mime};base64,{encoded}"
        merged_str = str(merged)
        merged_str = merged_str.replace(str(asset_file.relative_to(OUTPUT_DIR)), data_url)
        merged = BeautifulSoup(merged_str, "html.parser")
    for link in merged.find_all("link", rel="stylesheet"):
        href = link.get("href", "")
        if href.startswith("data:"):
            css_data = re.sub("^data:.*?;base64,", "", href)
            decoded = base64.b64decode(css_data).decode("utf-8", errors="ignore")
            style_tag = merged.new_tag("style")
            style_tag.string = decoded
            link.replace_with(style_tag)
    for script in merged.find_all("script", src=True):
        src = script["src"]
        if src.startswith("data:"):
            js_data = re.sub("^data:.*?;base64,", "", src)
            decoded = base64.b64decode(js_data).decode("utf-8", errors="ignore")
            new_script = merged.new_tag("script")
            new_script.string = decoded
            script.replace_with(new_script)
    out_file = OUTPUT_DIR / "single_page_local.html"
    out_file.write_text(str(merged), encoding="utf-8")
    print("\nCreated:", out_file)


if __name__ == "__main__":
    for path in cwd.rglob("*"):
        if path.suffix.lower() in {".html", ".htm"} and "output" not in path.parts:
            process_html(path)
    build_single_page()
    print("\nDONE — all assets extracted, deduped, hashed, and packed!")
