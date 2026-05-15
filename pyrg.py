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
import argparse
import fnmatch
import operator
import re
import sys
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dh import get_files, is_binary

cwd = Path.cwd()
IGNORED_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".ruff_cache", ".pytest_cache", ".mypy_cache"}
BINARY_CHUNK = 32768
DEFAULT_THREADS = 4
ANSI_BOLD = "\x1b[1m"
ANSI_RESET = "\x1b[0m"
ANSI_HIGHLIGHT = "\x1b[31m"


def colorize(text: str, start: int, end: int, enable: bool = True) -> str:
    if not enable:
        return text
    return text[:start] + ANSI_HIGHLIGHT + ANSI_BOLD + text[start:end] + ANSI_RESET + text[end:]


def matches_any_glob(path: Path, patterns: Iterable[str]) -> bool:
    basename = path.name
    return any((fnmatch.fnmatch(path, p) or fnmatch.fnmatch(basename, p) for p in patterns))


def search_file_text_mode(
    path: Path,
    regex: re.Pattern | None,
    fixed: str | None,
    ignore_case: bool,
    show_line_numbers: bool,
    color: bool,
    max_matches: int | None = None,
) -> tuple[str, list[tuple[int, str, list[tuple[int, int]]]]]:
    matches = []
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for lineno, raw_line in enumerate(fh, start=1):
                line = raw_line.rstrip("\n")
                spans: list[tuple[int, int]] = []
                if regex:
                    spans.extend(((m.start(), m.end()) for m in regex.finditer(line)))
                else:
                    hay = line.lower() if ignore_case else line
                    needle = fixed.lower() if ignore_case else fixed
                    start = 0
                    while True:
                        idx = hay.find(needle, start)
                        if idx == -1:
                            break
                        spans.append((idx, idx + len(needle)))
                        start = idx + max(1, len(needle))
                if spans:
                    matches.append((lineno, line, spans))
                    if max_matches and len(matches) >= max_matches:
                        break
    except Exception:
        return (path.relative_to(cwd), [])
    return (path.relative_to(cwd), matches)


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ripgrep-like recursive search in Python")
    p.add_argument("pattern", nargs="?", help="Regex pattern (positional) or use -e")
    p.add_argument("-e", "--regexp", dest="pattern_e", help="Pattern (alternative to positional)")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Case-insensitive search")
    p.add_argument("--fixed-strings", action="store_true", default=True, help="Fixed string search (no regex)")
    p.add_argument("-n", "--line-number", default=True, action="store_true", help="Show line numbers")
    p.add_argument("-l", "--files-with-matches", action="store_true", help="Only print filenames that match")
    p.add_argument("-c", "--count", action="store_true", help="Print count of matches per file")
    p.add_argument("-t", "--threads", type=int, default=DEFAULT_THREADS, help="Number of worker threads")
    p.add_argument("-H", "--hidden", action="store_true", default=True, help="Search hidden files and directories")
    p.add_argument("-g", "--glob", action="append", help="Include glob (fnmatch); can be repeated")
    p.add_argument("-x", "--exclude", action="append", help="Exclude glob (fnmatch); can be repeated")
    p.add_argument("-C", "--no-color", default=False, action="store_true", help="Disable colorized output")
    p.add_argument("-m", "--max-filesize", type=int, default=10000000, help="Skip files larger than size (bytes)")
    p.add_argument("-F", "--follow", default=False, action="store_true", help="Follow symlinks")
    p.add_argument("paths", nargs="*", default=["."], help="Files or directories to search (default: .)")
    return p


def main(argv: list[str] | None = None) -> int:
    cwd = Path.cwd()
    args = build_argparser().parse_args(argv)
    pattern = args.pattern_e or args.pattern
    if not pattern:
        print("No pattern provided. Use positional PATTERN or -e PATTERN.", file=sys.stderr)
        return 2
    ignore_case = args.ignore_case
    fixed = args.fixed_strings
    compiled = None
    if not fixed:
        flags = re.MULTILINE
        if ignore_case:
            flags |= re.IGNORECASE
        try:
            compiled = re.compile(pattern, flags)
        except re.error as ex:
            print(f"Invalid regex: {ex}", file=sys.stderr)
            return 2
    include_globs = args.glob or []
    exclude_globs = args.exclude or []
    candidates = get_files(cwd, include_hidden=True)
    if not candidates:
        return 0
    color = not args.no_color and sys.stdout.isatty()
    any_match = False
    results_per_file = {}

    def worker(path: str):
        if is_binary(path):
            return (path, [])
        return search_file_text_mode(
            path,
            regex=compiled,
            fixed=pattern if fixed else None,
            ignore_case=ignore_case,
            show_line_numbers=args.line_number,
            color=color,
        )

    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(worker, p): p for p in candidates}
        try:
            for fut in as_completed(futures):
                path, matches = fut.result()
                if not matches:
                    continue
                any_match = True
                results_per_file[path] = matches
                if args.files_with_matches:
                    print(path)
                elif args.count:
                    print(f"{path}:{len(matches)}")
                else:
                    for lineno, line, spans in matches:
                        out_line = line
                        if color and spans:
                            for s, e in sorted(spans, key=operator.itemgetter(0), reverse=True):
                                out_line = colorize(out_line, s, e, enable=True)
                        if args.line_number:
                            print(f"{path}:{lineno}:{out_line}")
                        else:
                            print(f"{path}:{out_line}")
        except KeyboardInterrupt:
            print("\nSearch cancelled.", file=sys.stderr)
            return 130
    return 0 if any_match else 1


if __name__ == "__main__":
    sys.exit(main())
