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
from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
import imagehash


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}


@dataclass(frozen=True)
class HashedImage:
    path: Path
    h: imagehash.ImageHash


def iter_image_paths(root: Path):
    # Recursive traversal with pathlib
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            yield p


def compute_hash(path: Path, hash_func: str, hash_size: int) -> HashedImage | None:
    try:
        # Many imagehash functions work best with RGB conversion
        with Image.open(path) as img:
            img = img.convert("RGB")

            if hash_func == "phash":
                h = imagehash.phash(img, hash_size=hash_size)
            elif hash_func == "dhash":
                h = imagehash.dhash(img, hash_size=hash_size)
            elif hash_func == "ahash":
                h = imagehash.average_hash(img, hash_size=hash_size)
            else:
                raise ValueError(f"Unknown hash_func: {hash_func}")

            return HashedImage(path=path, h=h)

    except Exception as e:
        # Skip unreadable/corrupt images
        print(f"[WARN] Skipping {path} ({e})")
        return None


def hash_distance(h1: imagehash.ImageHash, h2: imagehash.ImageHash) -> int:
    # imagehash.ImageHash implements subtraction as Hamming distance
    return int(h1 - h2)


def folderize_by_similarity(
    root: Path,
    out_dir_name: str,
    hash_func: str,
    hash_size: int,
    threshold: int,
    move: bool,
    copy_duplicates_to_group_only: bool,
):
    out_dir = root / out_dir_name
    out_dir.mkdir(parents=True, exist_ok=True)

    images: list[HashedImage] = []
    for p in iter_image_paths(root):
        # Avoid hashing images already moved/copied to output groups
        if out_dir_name in p.parts:
            continue
        hashed = compute_hash(p, hash_func=hash_func, hash_size=hash_size)
        if hashed is not None:
            images.append(hashed)

    if not images:
        print("No images found.")
        return

    # Greedy clustering:
    # - Each group has a representative hash (first member)
    # - Add image to first group where distance <= threshold
    # This is simple and works well for many practical cases.
    groups: list[dict] = []  # each: { "rep": ImageHash, "members": [HashedImage, ...] }

    for item in images:
        placed = False
        for g in groups:
            d = hash_distance(item.h, g["rep"])
            if d <= threshold:
                g["members"].append(item)
                placed = True
                break
        if not placed:
            groups.append({"rep": item.h, "members": [item]})

    # Create folders and move/copy
    group_idx = 0
    moved_or_copied = 0
    for g in groups:
        members = g["members"]

        # Skip singleton groups if you only care about duplicates/similar clusters
        if len(members) < 2:
            continue

        group_idx += 1
        group_folder = out_dir / f"group_{group_idx:06d}"
        group_folder.mkdir(parents=True, exist_ok=True)

        for mi, member in enumerate(members):
            dest = group_folder / member.path.name

            # Optional: if destination exists, avoid collision
            # by adding a suffix.
            if dest.exists():
                stem = dest.stem
                suffix = dest.suffix
                k = 1
                while True:
                    dest2 = group_folder / f"{stem}_{k}{suffix}"
                    if not dest2.exists():
                        dest = dest2
                        break
                    k += 1

            if move:
                shutil.move(str(member.path), str(dest))
            else:
                shutil.copy2(str(member.path), str(dest))

            moved_or_copied += 1

    print(f"Found {len(groups)} groups (including singletons).")
    print(f"Action complete: {moved_or_copied} files {'moved' if move else 'copied'} into {out_dir}.")


def main():
    parser = argparse.ArgumentParser(description="Folderize images by similarity using imagehash.")
    parser.add_argument("--root", type=str, default=".", help="Root directory to scan (default: current dir)")
    parser.add_argument("--out", type=str, default="_similar_groups", help="Output folder name")
    parser.add_argument("--hash-func", type=str, default="phash", choices=["phash", "dhash", "ahash"])
    parser.add_argument("--hash-size", type=int, default=16, help="Hash size (bigger = more sensitive).")
    parser.add_argument("--threshold", type=int, default=8, help="Max Hamming distance to consider similar.")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    # copy_duplicates_to_group_only is kept for extensibility; currently not used.
    folderize_by_similarity(
        root=root,
        out_dir_name=args.out,
        hash_func=args.hash_func,
        hash_size=args.hash_size,
        threshold=args.threshold,
        move=args.move,
        copy_duplicates_to_group_only=False,
    )


if __name__ == "__main__":
    main()
