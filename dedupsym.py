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
import os
import shutil
from collections import defaultdict
from pathlib import Path

import xxhash

CACHE_PATH = Path.home() / ".cache" / "dups_cache.json"
DUPS_DIR = Path.home() / ".cache" / "dups"
MANIFEST_PATH = DUPS_DIR / "manifest.json"
READ_CHUNK = 1024 * 8


def load_json(path):
    try:
        with Path(path).open(encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def xxh64_of_path(p: Path):
    h = xxhash.xxh64()
    with p.open("rb") as f:
        while True:
            chunk = f.read(READ_CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def build_groups(root: Path, cache: dict):
    groups = defaultdict(list)
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            fp = Path(dirpath) / name
            if ".git" in fp.parts:
                continue
            if fp.is_symlink():
                continue
            try:
                st = fp.stat()
            except Exception:
                continue
            if not fp.is_file():
                continue
            key = str(fp)
            size = st.st_size
            mtime = st.st_mtime
            cached = cache.get(key)
            if cached and cached.get("size") == size and (cached.get("mtime") == mtime):
                h = cached["hash"]
            else:
                try:
                    h = xxh64_of_path(fp)
                except Exception:
                    continue
                cache[key] = {"size": size, "mtime": mtime, "hash": h}
            groups[h].append(fp)
    return groups


def dedupe(root: Path, dry_run=False, force=False):
    cache = load_json(CACHE_PATH) if CACHE_PATH.exists() else {}
    groups = build_groups(root, cache)
    save_json(CACHE_PATH, cache)
    DUPS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_json(MANIFEST_PATH) if MANIFEST_PATH.exists() else {}
    changed = False
    for h, paths in groups.items():
        if len(paths) < 2:
            continue
        paths_sorted = sorted(paths, key=str)
        original = paths_sorted[0]
        stored_name = f"{h}__{original.name}"
        stored_path = DUPS_DIR / stored_name
        if not stored_path.exists():
            if dry_run:
                print(f"[DRY] move: {original} -> {stored_path}")
            else:
                stored_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(original), str(stored_path))
                print(f"moved: {original} -> {stored_path}")
            changed = True
        elif original.exists():
            if dry_run:
                print(f"[DRY] remove original file before symlink: {original}")
            else:
                original.unlink()
                print(f"removed original file: {original}")
        for p in paths_sorted[1:]:
            if p.is_symlink():
                continue
            if dry_run:
                print(f"[DRY] symlink: {p} -> {stored_path.resolve()}")
            else:
                if p.exists():
                    try:
                        p.unlink()
                    except Exception as e:
                        print(f"warning: could not remove {p}: {e}")
                        continue
                p.parent.mkdir(parents=True, exist_ok=True)
                Path(str(p)).symlink_to(str(stored_path.resolve()))
                print(f"symlinked: {p} -> {stored_path.resolve()}")
            changed = True
        manifest[str(stored_path)] = {"hash": h, "originals": [str(p) for p in paths_sorted]}
    if not dry_run and changed:
        save_json(MANIFEST_PATH, manifest)
        save_json(CACHE_PATH, cache)
        print(f"manifest written to {MANIFEST_PATH}")
    elif dry_run:
        print("dry-run complete; no changes written.")


def restore(dry_run=False):
    if not MANIFEST_PATH.exists():
        print("No manifest found at ~/dups/manifest.json")
        return
    manifest = load_json(MANIFEST_PATH)
    for stored_str, info in manifest.items():
        stored = Path(stored_str)
        if not stored.exists():
            print(f"stored file missing: {stored}")
            continue
        originals = [Path(p) for p in info.get("originals", [])]
        for orig in originals:
            if orig.exists() and (not orig.is_symlink()):
                print(f"skipping restore for {orig} (exists and not a symlink)")
                continue
            if orig.is_symlink():
                try:
                    target = Path(Path(orig).readlink())
                except Exception:
                    print(f"skipping {orig} (broken symlink)")
                    continue
                if target.resolve() != stored.resolve():
                    print(f"skipping {orig} (symlink points elsewhere)")
                    continue
            if dry_run:
                print(f"[DRY] restore {stored} -> {orig}")
            else:
                if orig.exists() or orig.is_symlink():
                    try:
                        orig.unlink()
                    except Exception as e:
                        print(f"warning: could not remove {orig}: {e}")
                        continue
                orig.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(stored, orig)
                print(f"restored: {orig}")
        if dry_run:
            print(f"[DRY] remove stored file {stored}")
        else:
            try:
                stored.unlink()
                print(f"removed stored file: {stored}")
            except Exception as e:
                print(f"warning: could not remove stored file {stored}: {e}")
    if not dry_run:
        try:
            MANIFEST_PATH.unlink()
            print(f"removed manifest: {MANIFEST_PATH}")
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser(
        description="Deduplicate files by moving one copy to ~/dups and symlinking duplicates using xxhash."
    )
    ap.add_argument("path", nargs="?", default=".", help="Path to scan (default current directory)")
    ap.add_argument("--dry-run", action="store_true", help="Show actions without making changes")
    ap.add_argument("--restore", action="store_true", help="Restore files from ~/dups using manifest")
    ap.add_argument("--force", action="store_true", help="Force overwrite behavior (not used for safety here)")
    args = ap.parse_args()
    root = Path(args.path).resolve()
    if args.restore:
        restore(dry_run=args.dry_run)
    else:
        dedupe(root, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
