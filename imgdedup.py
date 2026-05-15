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
from pathlib import Path

import cv2
import numpy as np
from imutils import paths


def dhash(image, hashSize=8):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hashSize + 1, hashSize))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum((2**i for i, v in enumerate(diff.flatten()) if v))


def compute_hashes(dataset_path, hashSize=8):
    hashes = {}
    imagePaths = list(paths.list_images(dataset_path))
    for imagePath in imagePaths:
        image = cv2.imread(imagePath)
        if image is None:
            print(f"[WARN] unable to read image: {imagePath}")
            continue
        try:
            h = dhash(image, hashSize=hashSize)
        except Exception as e:
            print(f"[WARN] failed to hash {imagePath}: {e}")
            continue
        hashes.setdefault(h, []).append(imagePath)
    return hashes


def main():
    ap = argparse.ArgumentParser(
        prog="imgdedup",
        description="Find and remove visually duplicate images using perceptual hashing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\nExamples:\n  imgdedup ./photos\n  imgdedup ./photos --remove\n        ",
    )
    ap.add_argument("path", help="path to image directory to scan")
    ap.add_argument(
        "--dry-run", action="store_true", default=True, help="preview duplicates without deleting (default: True)"
    )
    ap.add_argument("--remove", action="store_true", help="actually delete duplicate images")
    args = vars(ap.parse_args())
    dataset_path = args["path"]
    if not Path(dataset_path).is_dir():
        msg = f"[ERROR] dataset path does not exist or is not a directory: {dataset_path}"
        raise SystemExit(msg)
    is_remove_mode = args["remove"]
    print("[INFO] computing image hashes...")
    hashes = compute_hashes(dataset_path)
    if not hashes:
        print("[INFO] no images found in directory")
        return
    print(f"[INFO] found {len(hashes)} unique image(s)")
    for h, hashedPaths in hashes.items():
        if len(hashedPaths) > 1:
            if not is_remove_mode:
                montage = None
                for p in hashedPaths:
                    image = cv2.imread(p)
                    if image is None:
                        print(f"[WARN] unable to read image for montage: {p}")
                        continue
                    image = cv2.resize(image, (900, 900))
                    montage = image if montage is None else np.hstack([montage, image])
                print(f"[INFO] found {len(hashedPaths) - 1} duplicates with hash: {h}")
            else:
                print(f"[INFO] removing {len(hashedPaths) - 1} duplicates with hash: {h}")
                for p in hashedPaths[1:]:
                    Path(p).unlink()


if __name__ == "__main__":
    main()
