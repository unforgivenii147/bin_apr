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

import os
import re
from pathlib import Path


OUTPUT_DIR = Path("output")
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(exist_ok=True)


def extract_code_snippets_with_details(markdown_content):
    snippets_data = []
    lines = markdown_content.splitlines()
    in_code_block = False
    current_block_lines = []
    start_line_num = -1
    language = ""
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            if in_code_block:
                snippets_data.append(
                    {
                        "language": language,
                        "start_line": start_line_num,
                        "end_line": i,
                        "content": "\n".join(current_block_lines),
                    }
                )
                in_code_block = False
                current_block_lines = []
                language = ""
            else:
                in_code_block = True
                start_line_num = i + 1
                match = re.match("```(\\w*)", line.strip())
                if match and match.group(1):
                    language = match.group(1).lower()
                else:
                    language = ""
                current_block_lines = []
        elif in_code_block:
            current_block_lines.append(line)
    if in_code_block:
        snippets_data.append(
            {
                "language": language,
                "start_line": start_line_num,
                "end_line": len(lines),
                "content": "\n".join(current_block_lines),
            }
        )
    return snippets_data


def get_extension_from_language(language):
    extensions = {
        "sh": ".sh",
        "bash": ".sh",
        "zsh": ".sh",
        "python": ".py",
        "py": ".py",
        "javascript": ".js",
        "js": ".js",
        "html": ".html",
        "css": ".css",
        "json": ".json",
        "yaml": ".yaml",
        "yml": ".yaml",
        "sql": ".sql",
        "md": ".md",
        "text": ".txt",
        "plain": ".txt",
        "": ".txt",
    }
    return extensions.get(language.lower(), ".txt")


def process_markdown_files(directory="."):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".md", ".markdown", ".metadata", "METADATA", "PKGINFO", "PKG-INFO")):
                filepath = os.path.join(root, file)
                try:
                    content = Path(filepath).read_text(encoding="utf-8")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
                    continue
                code_details = extract_code_snippets_with_details(content)
                if code_details:
                    base_name = os.path.splitext(file)[0]
                    for _i, details in enumerate(code_details):
                        line_range = f"{details['start_line']}-{details['end_line']}"
                        language = details["language"]
                        extension = get_extension_from_language(language)
                        output_filename = f"output/{base_name}_lines_{line_range}{extension}"
                        output_path = os.path.join(root, output_filename)
                        Path(output_path).write_text(details["content"].strip(), encoding="utf-8")
                        print(
                            f"Saved snippet from {filepath} (Lines {line_range}, Lang: '{language}') to {output_path}"
                        )


if __name__ == "__main__":
    process_markdown_files()
