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
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from loguru import logger
from xxhash import xxh64

DEFAULT_BLOCK = 32768
QUICK_READ = 4096


def file_stat_key(p: Path):
    try:
        st = p.stat()
        return (st.st_ino, st.st_dev)
    except Exception:
        return None


def quick_hash(path: Path, n=QUICK_READ):
    h = xxh64()
    try:
        size = path.stat().st_size
        with path.open("rb") as f:
            head = f.read(n)
            h.update(head)
            if size > n * 2:
                f.seek(max(size - n, 0))
                tail = f.read(n)
                h.update(tail)
            else:
                f.seek(0)
                rest = f.read()
                h.update(rest)
    except Exception as e:
        msg = f"quick_hash error {path}: {e}"
        raise OSError(msg)
    return h.hexdigest()


def full_hash(path: Path, block_size=DEFAULT_BLOCK):
    h = xxh64()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(block_size), b""):
                h.update(chunk)
    except Exception as e:
        msg = f"full_hash error {path}: {e}"
        raise OSError(msg)
    return h.hexdigest()


def iter_files(root: Path, recursive: bool, follow_symlinks: bool, min_size: int):
    if recursive:
        for p in root.rglob("*"):
            if p.is_file() and (follow_symlinks or not p.is_symlink()):
                try:
                    if p.stat().st_size >= min_size:
                        yield p
                except Exception:
                    continue
    else:
        for p in root.iterdir():
            if p.is_file() and (follow_symlinks or not p.is_symlink()):
                try:
                    if p.stat().st_size >= min_size:
                        yield p
                except Exception:
                    continue


def choose_keep(files, policy="oldest"):
    if policy == "first":
        return min(files, key=str)
    if policy == "oldest":
        return min(files, key=lambda p: p.stat().st_mtime)
    if policy == "newest":
        return max(files, key=lambda p: p.stat().st_mtime)
    return min(files, key=str)


def main() -> None:
    cwd = Path.cwd()
    p = argparse.ArgumentParser(description="Find and delete duplicate files by content.")
    p.add_argument(
        "-r", "--recursive", default=True, action="store_true", help="Search directories recursively (default: False)."
    )
    p.add_argument(
        "-n", "--dry-run", default=False, action="store_true", help="Don't delete; just show what would be done."
    )
    p.add_argument("--follow-symlinks", default=False, action="store_true", help="Follow symlinks to files.")
    p.add_argument(
        "--min-size", type=int, default=1, help="Minimum file size (bytes) to consider. Default 1 (skip zero-size)."
    )
    p.add_argument(
        "-k",
        "--keep",
        choices=("first", "oldest", "newest"),
        default="first",
        help="Which file to keep within duplicates.",
    )
    args = p.parse_args()
    root = Path.cwd()
    size_groups = defaultdict(list)
    total_files = 0
    for f in iter_files(root, args.recursive, args.follow_symlinks, args.min_size):
        total_files += 1
        try:
            size_groups[f.stat().st_size].append(f)
        except Exception:
            continue
    candidates_by_size = {s: lst for s, lst in size_groups.items() if len(lst) > 1}
    if not candidates_by_size:
        print("No potential duplicates found (no groups with equal size).")
        return
    print(
        f"Found {sum((len(v) for v in candidates_by_size.values()))} files in {len(candidates_by_size)} size-groups to examine."
    )
    quick_groups = defaultdict(list)
    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = {}
        for files in candidates_by_size.values():
            for fpath in files:
                futures[ex.submit(quick_hash, fpath)] = fpath
        for fut in as_completed(futures):
            fpath = futures[fut]
            try:
                h = fut.result()
                key = (fpath.stat().st_size, h)
                quick_groups[key].append(fpath)
            except Exception as e:
                print(f"Skipping {fpath}: {e}")
    need_full = [group for group in quick_groups.values() if len(group) > 1]
    if not need_full:
        print("No dups")
        return
    full_groups = defaultdict(list)
    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = {}
        for group in need_full:
            for fpath in group:
                st_key = file_stat_key(fpath)
                futures[ex.submit(full_hash, fpath)] = (fpath, st_key)
        for fut in as_completed(futures):
            fpath, st_key = futures[fut]
            try:
                h = fut.result()
                full_groups[h].append((fpath, st_key))
            except Exception as e:
                print(f"Skipping {fpath}: {e}")
    to_delete = []
    for h, entries in full_groups.items():
        inode_map = {}
        for p, stk in entries:
            inode_map.setdefault(stk, []).append(p)
        group_reps = [min(ps) for ps in inode_map.values()]
        if len(group_reps) < 2:
            continue
        keep_file = choose_keep(group_reps, policy=args.keep)
        for ps in group_reps:
            if ps == keep_file:
                continue
            to_delete.append(ps)
    if not to_delete:
        print("No dups")
        return
    print(f"Planned deletions: {len(to_delete)} files.")
    for p in to_delete:
        print("  " + str(p))
    if args.dry_run:
        print("Dry-run enabled; no files were deleted.")
        return
    removed = 0
    failed = 0
    for p in to_delete:
        try:
            p.unlink()
            print(f"Deleted: {p.relative_to(cwd)}")
            removed += 1
        except Exception as e:
            print(f"Failed to delete {p.relative_to(cwd)}: {e}")
            failed += 1
    if failed:
        print(f"Removed: {removed}. Failed: {failed}.")
    else:
        logger.debug(f"Removed: {removed}")


if __name__ == "__main__":
    main()
