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

import base64
import os
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup


def encode_local_file_to_base64(file_path):
    try:
        with Path(file_path).open("rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Internal Error: encode_local_file_to_base64 called with non-existent file: {file_path}")
        return None
    except Exception as e:
        print(f"Error encoding file {file_path}: {e}")
        return None


def find_local_resource(resource_name, base_html_dir):
    search_paths = [Path("/sdcard/_static"), Path(base_html_dir), Path.cwd(), Path(base_html_dir).parent.parent]
    normalized_resource_name = resource_name
    if normalized_resource_name.startswith("/"):
        normalized_resource_name = normalized_resource_name.lstrip("/")
    for search_dir in search_paths:
        abs_search_dir = Path(str(search_dir)).resolve()
        potential_path = os.path.join(abs_search_dir, normalized_resource_name)
        if Path(potential_path).exists():
            print(f"Found resource '{resource_name}' at: {potential_path}")
            return potential_path
        path_relative_to_html_dir = os.path.join(base_html_dir, resource_name)
        if Path(path_relative_to_html_dir).exists():
            print(f"Found resource '{resource_name}' relative to HTML dir: {path_relative_to_html_dir}")
            return path_relative_to_html_dir
        if resource_name.startswith("/"):
            path_stripped_slash = os.path.join(base_html_dir, resource_name.lstrip("/"))
            if Path(path_stripped_slash).exists():
                print(f"Found resource '{resource_name}' (stripped slash) relative to HTML dir: {path_stripped_slash}")
                return path_stripped_slash
        fallback_search_dirs = [Path.cwd(), os.path.join(Path.cwd(), os.pardir), os.path.join(base_html_dir, os.pardir)]
        for fallback_dir in fallback_search_dirs:
            abs_fallback_dir = Path(fallback_dir).resolve()
            potential_path = os.path.join(abs_fallback_dir, resource_name)
            if Path(potential_path).exists():
                print(f"Found resource '{resource_name}' in fallback dir {abs_fallback_dir}: {potential_path}")
                return potential_path
            if resource_name.startswith("/"):
                potential_path_stripped = os.path.join(abs_fallback_dir, resource_name.lstrip("/"))
                if Path(potential_path_stripped).exists():
                    print(
                        f"Found resource '{resource_name}' (stripped slash) in fallback dir {abs_fallback_dir}: {potential_path_stripped}"
                    )
                    return potential_path_stripped
    print(f"Resource '{resource_name}' not found in primary or fallback locations.")
    return None


def make_html_standalone(path):
    html_content = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    base_html_dir = str(path.parent)
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if src and (not src.startswith(("http://", "https://", "data:"))):
            local_img_path = find_local_resource(src, base_html_dir)
            if local_img_path:
                encoded_img = encode_local_file_to_base64(local_img_path)
                if encoded_img:
                    img_tag["src"] = f"data:{get_mime_type(local_img_path)};base64,{encoded_img}"
            else:
                print(f"Warning: Image resource '{src}' not found, removing tag.")
                img_tag.decompose()
    for link_tag in soup.find_all("link"):
        if link_tag.get("rel") == ["stylesheet"]:
            href = link_tag.get("href")
            if href and (not href.startswith(("http://", "https://", "data:"))):
                local_css_path = find_local_resource(href, base_html_dir)
                if local_css_path:
                    print(f"Processing CSS file: {local_css_path}")
                    try:
                        css_content = Path(local_css_path).read_text(encoding="utf-8")
                        font_url_matches = re.findall(
                            "url\\s*\\(\\s*[\\'\"]?([^\\'\"\\)]+)[\\'\"]?\\s*\\)", css_content
                        )
                        for font_url in font_url_matches:
                            if not font_url.startswith(("http://", "https://", "data:")):
                                local_font_path = find_local_resource(font_url, Path(local_css_path).parent)
                                if local_font_path:
                                    encoded_font = encode_local_file_to_base64(local_font_path)
                                    if encoded_font:
                                        mime_type = get_mime_type(local_font_path)
                                        css_content = re.sub(
                                            re.escape(f"url({font_url})").replace("\\(", "\\(").replace("\\)", "\\)"),
                                            f"url('data:{mime_type};base64,{encoded_font}')",
                                            css_content,
                                            flags=re.IGNORECASE,
                                        )
                                else:
                                    print(
                                        f"Warning: Font file '{font_url}' referenced in CSS not found, leaving reference."
                                    )
                        style_tag = soup.new_tag("style")
                        style_tag.string = css_content
                        link_tag.replace_with(style_tag)
                    except Exception as e:
                        print(f"Error processing CSS file {local_css_path}: {e}")
                        link_tag.decompose()
                else:
                    print(f"Warning: CSS resource '{href}' not found, removing link tag.")
                    link_tag.decompose()
    for style_tag in soup.find_all("style"):
        style_content = style_tag.string
        if style_content:
            font_url_matches = re.findall("url\\s*\\(\\s*[\\'\"]?([^\\'\"\\)]+)[\\'\"]?\\s*\\)", style_content)
            for font_url in font_url_matches:
                if not font_url.startswith(("http://", "https://", "data:")):
                    local_font_path = find_local_resource(font_url, base_html_dir)
                    if local_font_path:
                        encoded_font = encode_local_file_to_base64(local_font_path)
                        if encoded_font:
                            mime_type = get_mime_type(local_font_path)
                            style_content = re.sub(
                                re.escape(f"url({font_url})").replace("\\(", "\\(").replace("\\)", "\\)"),
                                f"url('data:{mime_type};base64,{encoded_font}')",
                                style_content,
                                flags=re.IGNORECASE,
                            )
                    else:
                        print(
                            f"Warning: Font file '{font_url}' referenced in inline style not found, leaving reference."
                        )
            style_tag.string = style_content
    for script_tag in soup.find_all("script"):
        src = script_tag.get("src")
        if src and (not src.startswith(("http://", "https://", "data:"))):
            local_script_path = find_local_resource(src, base_html_dir)
            if local_script_path:
                try:
                    script_content = Path(local_script_path).read_text(encoding="utf-8")
                    script_tag.string = script_content
                    script_tag["src"] = ""
                except Exception as e:
                    print(f"Error reading script content from {local_script_path}: {e}")
                    script_tag.decompose()
            else:
                print(f"Warning: Local script resource '{src}' not found, removing tag.")
                script_tag.decompose()
        elif not src:
            pass
        elif src.startswith(("http://", "https://")):
            print(f"Removing external script: {src}")
            script_tag.decompose()
    return soup.prettify()


def get_mime_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".otf": "font/otf",
        ".eot": "application/vnd.ms-fontobject",
        ".js": "application/javascript",
        ".css": "text/css",
    }
    return mime_map.get(ext, "application/octet-stream")


if __name__ == "__main__":
    input_path = Path(sys.argv[1])
    output_file = input_path.stem + "_standalone" + input_path.suffix
    output_path = input_path.with_name(output_file)
    standalone_html = make_html_standalone(input_path)
    if standalone_html:
        try:
            output_path.write_text(standalone_html, encoding="utf-8")
            print(f"Standalone HTML saved to: {output_file}")
        except Exception as e:
            print(f"Error writing to output file {output_file}: {e}")
