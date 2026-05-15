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

import argparse
import json
from pathlib import Path

import nbformat as nbf


def py_to_ipynb(input_file, output_file=None):
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found.")
        return False
    code = Path(input_file).read_text(encoding="utf-8")
    nb = nbf.v4.new_notebook()
    cells = []
    current_cell = []
    lines = code.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if (
            i > 0
            and (
                line.startswith(("def ", "class "))
                or (line.startswith(("import ", "from ")) and (not current_cell[-1].startswith(("import ", "from "))))
                or (
                    line.strip() == ""
                    and current_cell
                    and (i + 1 < len(lines))
                    and lines[i + 1].strip()
                    and (not lines[i + 1].startswith((" ", "\t")))
                )
            )
            and current_cell
        ):
            cell_code = "\n".join(current_cell).strip()
            if cell_code:
                cells.append(nbf.v4.new_code_cell(cell_code))
            current_cell = []
        current_cell.append(line.rstrip())
        i += 1
    if current_cell:
        cell_code = "\n".join(current_cell).strip()
        if cell_code:
            cells.append(nbf.v4.new_code_cell(cell_code))
    nb["cells"] = cells
    if output_file is None:
        output_file = Path(input_file).stem + ".ipynb"
    with Path(output_file).open("w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"Successfully converted '{input_file}' to '{output_file}'")
    print(f"Created {len(cells)} cell(s)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Convert a Python script to a Jupyter notebook")
    parser.add_argument("input", help="Input Python file (.py)")
    parser.add_argument("output", nargs="?", help="Output notebook file (.ipynb) (optional)")
    parser.add_argument("--no-split", action="store_true", help="Don't split code into multiple cells (one cell only)")
    args = parser.parse_args()
    if args.no_split:
        code = Path(args.input).read_text(encoding="utf-8")
        nb = nbf.v4.new_notebook()
        nb["cells"] = [nbf.v4.new_code_cell(code)]
        output_file = args.output or Path(args.input).stem + ".ipynb"
        with Path(output_file).open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"Successfully converted '{args.input}' to '{output_file}' (single cell)")
    else:
        py_to_ipynb(args.input, args.output)


if __name__ == "__main__":
    main()
