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
import sys
from pathlib import Path

import cv2
import numpy as np

THRESHOLD = 0.8


def hash_similarity(hash1: np.ndarray, hash2: np.ndarray) -> float:
    """
    Compute similarity between two OpenCV hashes.
    Returns value between 0 and 1 (1 = identical).
    """
    dist = cv2.norm(hash1, hash2, cv2.NORM_HAMMING)
    max_bits = hash1.size * 8
    similarity = 1.0 - (dist / max_bits)
    return similarity


def gif_to_unique_jpg(gif_path: Path):
    if not gif_path.exists():
        raise FileNotFoundError(f"File not found: {gif_path}")

    if gif_path.suffix.lower() != ".gif":
        raise ValueError("Input file must be a .gif")

    output_dir = gif_path.parent / gif_path.stem
    output_dir.mkdir(exist_ok=True)

    cap = cv2.VideoCapture(str(gif_path))
    if not cap.isOpened():
        raise RuntimeError("Failed to open GIF")

    hasher = cv2.img_hash.AverageHash_create()

    saved_count = 0
    frame_index = 0
    previous_hash = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_hash = hasher.compute(frame)

        save_frame = True
        if previous_hash is not None:
            similarity = hash_similarity(previous_hash, current_hash)
            if similarity >= THRESHOLD:
                save_frame = False

        if save_frame:
            output_file = output_dir / f"{gif_path.stem}_{saved_count:04d}.jpg"
            cv2.imwrite(str(output_file), frame)
            previous_hash = current_hash
            saved_count += 1

        frame_index += 1

    cap.release()

    print(f"✅ Saved {saved_count} unique frames to: {output_dir}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python gif_to_jpg_unique.py <input.gif>")
        sys.exit(1)

    gif_path = Path(sys.argv[1])
    gif_to_unique_jpg(gif_path)


if __name__ == "__main__":
    main()
