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

import curses
from pathlib import Path

LINES_PER_FILE = 20


def list_files():
    return sorted([p for p in Path().iterdir() if p.is_file()], key=lambda p: p.name.lower())


def head_lines(path, n):
    lines = []
    try:
        with Path(path).open(encoding="utf-8", errors="replace") as f:
            for _ in range(n):
                line = f.readline()
                if not line:
                    break
                lines.append(line.rstrip("\n"))
    except Exception as e:
        lines = [f"[Error reading file: {e}]"]
    return lines


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)


def draw(stdscr, files, idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    header = f"File {idx + 1}/{len(files)}: {files[idx].name}"
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addnstr(0, 0, header, w - 1)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    lines = head_lines(files[idx], LINES_PER_FILE)
    for i, line in enumerate(lines, start=2):
        if i >= h - 1:
            break
        if line.startswith("[Error"):
            stdscr.attron(curses.color_pair(4))
            stdscr.addnstr(i, 0, line, w - 1)
            stdscr.attroff(curses.color_pair(4))
        else:
            stdscr.attron(curses.color_pair(2))
            stdscr.addnstr(i, 0, line, w - 1)
            stdscr.attroff(curses.color_pair(2))
    footer = "PgDown: next | PgUp: prev | q: quit"
    stdscr.attron(curses.color_pair(3))
    stdscr.addnstr(h - 1, 0, footer, w - 1)
    stdscr.attroff(curses.color_pair(3))
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    init_colors()
    files = list_files()
    if not files:
        stdscr.addstr(0, 0, "No files in directory.")
        stdscr.getch()
        return
    idx = 0
    draw(stdscr, files, idx)
    while True:
        key = stdscr.getch()
        if key in {ord("q"), ord("Q")}:
            break
        if key == curses.KEY_NPAGE:
            if idx < len(files) - 1:
                idx += 1
                draw(stdscr, files, idx)
        elif key == curses.KEY_PPAGE and idx > 0:
            idx -= 1
            draw(stdscr, files, idx)


if __name__ == "__main__":
    curses.wrapper(main)
