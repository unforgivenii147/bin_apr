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
import sys
from pathlib import Path


def read_man_file(filename):
    try:
        with Path(filename).open(encoding="utf-8", errors="ignore") as f:
            return f.read()
    except FileNotFoundError:
        sys.exit(f"Error: file {filename} not found")


def man_to_markdown(content):
    lines = content.splitlines()
    md_lines = []
    in_code_block = False
    pending_tp = None
    for line in lines:
        if line.startswith(".TH"):
            continue
        if line.startswith(".SH"):
            header = line[3:].strip()
            md_lines.append(f"# {header.title()}")
            continue
        if line.startswith(".SS"):
            subheader = line[3:].strip()
            md_lines.append(f"## {subheader.title()}")
            continue
        line = re.sub("\\.B\\s+(.+)", "**\\1**", line)
        line = re.sub("\\.I\\s+(.+)", "*\\1*", line)
        if line.startswith(".BR"):
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                tokens = parts[1].split('"')
                formatted = []
                for i, t in enumerate(tokens):
                    if not t.strip():
                        continue
                    if i % 2 == 0:
                        formatted.append(f"**{t.strip()}**")
                    else:
                        formatted.append(t.strip())
                md_lines.append(" ".join(formatted))
                continue
        if line.startswith(".IR"):
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                tokens = parts[1].split('"')
                formatted = []
                for i, t in enumerate(tokens):
                    if not t.strip():
                        continue
                    if i % 2 == 0:
                        formatted.append(f"*{t.strip()}*")
                    else:
                        formatted.append(t.strip())
                md_lines.append(" ".join(formatted))
                continue
        if line.startswith(".PP"):
            md_lines.append("")
            continue
        if line.startswith(".IP"):
            parts = line.split(maxsplit=2)
            if len(parts) >= 2 and parts[1].isdigit():
                num = parts[1]
                item = parts[2] if len(parts) > 2 else ""
                md_lines.append(f"{num}. {item}")
                continue
            if len(parts) >= 2:
                item = parts[1] if len(parts) > 1 else ""
                rest = parts[2] if len(parts) > 2 else ""
                md_lines.append(f"- {item} {rest}".strip())
                continue
        if line.startswith(".TP"):
            pending_tp = True
            continue
        if pending_tp:
            term = line.strip()
            pending_tp = False
            md_lines.append(f"- {term}:")
            continue
        if line.startswith((".nf", ".RS", ".EX")):
            if not in_code_block:
                md_lines.append("```sh")
                in_code_block = True
            continue
        if line.startswith((".fi", ".RE", ".EE")):
            if in_code_block:
                md_lines.append("```")
                in_code_block = False
            continue
        if line.startswith("."):
            continue
        if re.match("^\\s*\\$", line) or re.match("^\\s*(ls|cat|grep|echo|pwd|cd|mkdir|rm|touch|man)\\b", line):
            if not in_code_block:
                md_lines.append("```sh")
                in_code_block = True
            md_lines.append(line)
            continue
        if in_code_block:
            md_lines.append("```")
            in_code_block = False
        line = re.sub("\\b(ls|cat|grep|echo|pwd|cd|mkdir|rm|touch|man)\\b", "`\\1`", line)
        md_lines.append(line)
    if in_code_block:
        md_lines.append("```")
    return "\n".join(md_lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: python man2md.py <manfile>")
        sys.exit(1)
    filename = sys.argv[1]
    raw = read_man_file(filename)
    markdown = man_to_markdown(raw)
    base, _ = os.path.splitext(filename)
    outname = base + ".md"
    Path(outname).write_text(markdown, encoding="utf-8")
    print(f"Converted {filename} → {outname}")


if __name__ == "__main__":
    main()
