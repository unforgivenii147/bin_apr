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

import argparse
import datetime
import grp
import os
import pwd
import stat
import sys
from pathlib import Path


COLORS = {"dir": "\x1b[34m", "link": "\x1b[36m", "exec": "\x1b[32m", "reset": "\x1b[0m"}


def use_color(mode: str) -> bool:
    if mode == "always":
        return True
    if mode == "never":
        return False
    return sys.stdout.isatty()


def colorize(name, st, enabled):
    if not enabled:
        return name
    if stat.S_ISDIR(st.st_mode):
        return f"{COLORS['dir']}{name}{COLORS['reset']}"
    if stat.S_ISLNK(st.st_mode):
        return f"{COLORS['link']}{name}{COLORS['reset']}"
    if st.st_mode & stat.S_IXUSR:
        return f"{COLORS['exec']}{name}{COLORS['reset']}"
    return name


def human_size(size):
    for unit in ("B", "K", "M", "G", "T"):
        if size < 1024:
            return f"{size}{unit}"
        size //= 1024
    return f"{size}P"


def indicator(path, st):
    if stat.S_ISDIR(st.st_mode):
        return "/"
    if stat.S_ISLNK(st.st_mode):
        return "@"
    if st.st_mode & stat.S_IXUSR:
        return "*"
    return ""


def format_time(ts, full):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M:%S" if full else "%b %d %H:%M")


def format_entry(entry, args, color_enabled):
    try:
        st = entry.stat(follow_symlinks=args.L)
    except FileNotFoundError:
        return ""
    name = entry.name
    name = colorize(name, st, color_enabled)
    if args.p and entry.is_dir():
        name += "/"
    if args.F:
        name += indicator(entry, st)
    inode = f"{st.st_ino} " if args.i else ""
    blocks = f"{st.st_blocks} " if args.s else ""
    if not args.l:
        return f"{inode}{blocks}{name}"
    perms = stat.filemode(st.st_mode)
    nlink = st.st_nlink
    uid = st.st_uid if args.n else pwd.getpwuid(st.st_uid).pw_name
    gid = st.st_gid if args.n else grp.getgrgid(st.st_gid).gr_name
    size = human_size(st.st_size) if args.h else st.st_size
    ts = st.st_ctime if args.lc else st.st_atime if args.lu else st.st_mtime
    time_str = format_time(ts, args.full_time)
    return f"{inode} {blocks} {perms}  {nlink}  {uid}  {gid}  {size: >6}  {time_str}  {name} "


def scan_dir(path, args):
    try:
        with os.scandir(path) as it:
            entries = [Path(e.path) for e in it]
    except PermissionError:
        print(f"ls: cannot open directory '{path}'", file=sys.stderr)
        return []
    if not args.a:
        if args.A:
            entries = [e for e in entries if e.name not in {".", ".."} and (not e.name.startswith("."))]
        else:
            entries = [e for e in entries if not e.name.startswith(".")]

    def key(p):
        try:
            st = p.stat(follow_symlinks=args.L)
        except FileNotFoundError:
            return 0
        if args.S:
            return -st.st_size
        if args.t:
            return -st.st_mtime
        if args.tc:
            return -st.st_ctime
        if args.tu:
            return -st.st_atime
        if args.X:
            return p.suffix
        return p.name

    entries.sort(key=key, reverse=args.r)
    if args.group_directories_first:
        entries.sort(key=lambda e: not e.is_dir())
    return entries


def print_columns(items, width, by_row):
    if not items:
        return
    max_len = max((len(i) for i in items)) + 2
    cols = max(1, width // max_len)
    rows = (len(items) + cols - 1) // cols
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c if by_row else c * rows + r
            if idx < len(items):
                print(items[idx].ljust(max_len), end="")
        print()


def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("-1", dest="one", action="store_true")
    p.add_argument("-a", action="store_true")
    p.add_argument("-A", action="store_true")
    p.add_argument("-x", action="store_true")
    p.add_argument("-d", action="store_true")
    p.add_argument("-L", action="store_true")
    p.add_argument("-H", action="store_true")
    p.add_argument("-R", action="store_true")
    p.add_argument("-p", action="store_true")
    p.add_argument("-F", action="store_true")
    p.add_argument("-l", action="store_true")
    p.add_argument("-i", action="store_true")
    p.add_argument("-n", action="store_true")
    p.add_argument("-s", action="store_true")
    p.add_argument("-h", action="store_true")
    p.add_argument("-lc", action="store_true")
    p.add_argument("-lu", action="store_true")
    p.add_argument("--full-time", action="store_true")
    p.add_argument("-S", action="store_true")
    p.add_argument("-X", action="store_true")
    p.add_argument("-v", action="store_true")
    p.add_argument("-t", action="store_true")
    p.add_argument("-tc", action="store_true")
    p.add_argument("-tu", action="store_true")
    p.add_argument("-r", action="store_true")
    p.add_argument("-w", type=int, default=80)
    p.add_argument("--group-directories-first", action="store_true")
    p.add_argument("--color", nargs="?", const="auto", default="auto")
    p.add_argument("paths", nargs="*", default=["."])
    args = p.parse_args()
    color_enabled = use_color(args.color)
    for path in args.paths:
        path = Path(path)
        if args.d or not path.is_dir():
            print(format_entry(path, args, color_enabled))
            continue
        entries = scan_dir(path, args)
        formatted = [format_entry(e, args, color_enabled) for e in entries]
        if args.l or args._get_kwargs():
            for f in formatted:
                print(f)
        elif args._1:
            print("\n".join(formatted))
        else:
            print_columns(formatted, args.w, args.x)
        if args.R:
            for e in entries:
                if e.is_dir() and (not e.is_symlink()):
                    print(f"\n{e}:")
                    main()


if __name__ == "__main__":
    main()
