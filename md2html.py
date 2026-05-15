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

import os
import re
import shutil
import sys
from pathlib import Path

import markdown
from bs4 import BeautifulSoup


def modify_classes(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    tag_class_map = {
        "h1": "text-4xl font-bold mt-4 mb-2",
        "h2": "text-4xl font-semibold mt-4 mb-2",
        "h3": "text-2xl font-medium mt-4 mb-2",
        "h4": "text-xl font-medium mt-4 mb-2",
        "p": "text-base leading-relaxed mt-2 mb-4",
        "code": "bg-gray-100 p-1 rounded-md",
        "pre": "bg-gray-900 text-white p-4 rounded-md overflow-x-auto",
    }
    for tag, tailwind_classes in tag_class_map.items():
        for element in soup.find_all(tag):
            existing_classes = element.get("class", [])
            new_classes = tailwind_classes.split()
            combined_classes = list(set(existing_classes + new_classes))
            element["class"] = combined_classes
    return str(soup)


def convert_latex_format(text):
    text = re.sub("\\\\\\[(.*?)\\\\\\]", '<div class="latex-display">\\1</div>', text, flags=re.DOTALL)
    return re.sub("\\\\\\((.*?)\\\\\\)", '<span class="latex-inline">\\1</span>', text, flags=re.DOTALL)


def read_markdown_file(file_path):
    with Path(file_path).open(encoding="utf-8", errors="ignore") as f:
        return f.read()


def convert_markdown(md_path: str) -> str:
    if not md_path:
        msg = "Markdown file path cannot be empty. Please provide a valid .md file path."
        raise ValueError(msg)
    markdown_text = read_markdown_file(md_path)
    markdown_text = convert_latex_format(markdown_text)
    base_name = Path(md_path).name.replace(".md", "")
    temp_html_path = os.path.join("/sdcard/tmp", f"{base_name}.html")
    final_output_path = md_path.replace(".md", ".html")
    html_content = markdown.markdown(
        markdown_text, extensions=["md_in_html", "fenced_code", "codehilite", "toc", "attr_list", "tables"]
    )
    html_content = modify_classes(html_content)
    html_template = f'\n    <!DOCTYPE html>\n    <html lang="en" class="scroll-smooth bg-gray-50 text-gray-900 antialiased">\n        <head>\n            <meta charset="UTF-8">\n            <meta name="viewport" content="width=device-width, initial-scale=1.0">\n            <title>{base_name}</title>\n            <link rel="stylesheet" href="/sdcard/_static/katex/tailwind.min.css">\n            <link rel="stylesheet" href="/sdcard/_static/katex/custom.css">\n            <link rel="stylesheet" href="/sdcard/_static/katex/katex.min.css">\n            <script src="/sdcard/_static/katex/tex.js"></script>\n            <script src="/sdcard/_static/katex/auto-render.min.js"></script>\n            <script src="/sdcard/_static/katex/katex.min.js"></script>\n        </head>\n        <body for="html-export" class="min-h-screen flex flex-col justify-between">\n            <main class="flex-1">\n                <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 prose prose-lg prose-slate">\n                    {html_content}\n                </div>\n            </main>\n        </body>\n    </html>\n    '
    Path(temp_html_path).write_text(html_template, encoding="utf-8")
    shutil.copy(temp_html_path, final_output_path)
    return final_output_path


if __name__ == "__main__":
    md_path = sys.argv[1]
    output_path = convert_markdown(md_path)
    print(f"Output saved in {output_path}")
