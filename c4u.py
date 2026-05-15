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

import contextlib
import html as _html
import re
import sys
import urllib.parse
from pathlib import Path

import requests
from packaging.version import Version
from termcolor import cprint


def save_output(content, pkg):
    Path(f"/sdcard/whl/json/{pkg}").write_text(content, encoding="utf-8")


def parse_version_obj(s):
    return Version(s)


def extract_links(html_text):
    pattern = re.compile("<a\\s+[^>]*href=([\"\\'])(?P<href>.*?)\\1[^>]*>(?P<text>.*?)</a>", re.IGNORECASE | re.DOTALL)
    for m in pattern.finditer(html_text):
        href = _html.unescape(m.group("href")).strip()
        text = _html.unescape(re.sub("<[^>]+>", "", m.group("text"))).strip()
        yield (href, text)


def filename_from_href(href):
    p = urllib.parse.urlparse(href)
    name = Path(p.path).name
    if not name:
        frag = p.fragment
        name = frag or p.netloc
    return name


def find_version_in_text(s):
    m = re.search("(?<![\\d.])(\\d+(?:\\.\\d+)+)(?![\\d.])", s)
    return m.group(1) if m else None


def ext_priority(fname) -> int:
    f = fname.lower()
    if f.endswith(".whl"):
        return 0
    if f.endswith((".tar.gz", ".tgz")):
        return 1
    if f.endswith((".zip", ".tar.bz2")):
        return 2
    return 3


def extract_latest_version_link(html_text):
    entries = []
    rev_html = html_text[::-1]
    target_line = ""
    for k in rev_html:
        if "<a href" in k:
            print(k)
            target_line = k
            break
    for href, text in extract_links(html_text):
        href = href.split('"')[0].split("'")[0]
        fname = filename_from_href(href) or text
        ver = find_version_in_text(fname) or find_version_in_text(text)
        if not ver:
            continue
        try:
            ver_obj = parse_version_obj(ver)
        except Exception:
            ver_obj = ver
        pr = ext_priority(fname)
        entries.append((ver_obj, pr, href, fname))
    if not entries:
        print("no versioned links found", file=sys.stderr)
        sys.exit(1)
    best = max(entries, key=lambda e: (e[0], -e[1]))
    return best[2]


def get_latest_pkg_version(pkg_name):
    try:
        url = f"https://mirror-pypi.runflare.com/{pkg_name}/json"
        html = requests.get(url, timeout=50).text
        save_output(html, pkg_name)
    except:
        return None
    wheel_pattern = re.compile(
        f"{re.escape(pkg_name)}-([0-9][A-Za-z0-9\\.\\-_]*)\\.(?:whl|tar\\.gz|zip)", re.IGNORECASE
    )
    versions = []
    for match in wheel_pattern.finditer(html):
        version_str = match.group(1)
        with contextlib.suppress(BaseException):
            versions.append(Version(version_str))
    latest_version_link = get_latest_pkg_version(html)
    if latest_version_link:
        with Path("/sdcard/pkgs_links").open("a", encoding="utf-8") as f:
            f.write(f"\n{latest_version_link}\n")
    return max(versions) if versions else None


if __name__ == "__main__":
    try:
        pkg = sys.argv[1]
        latest_version = get_latest_pkg_version(pkg)
        cprint(f"{pkg} : ", "green", end=" | ")
        cprint(f"{latest_version}", "cyan")
    except:
        pass
