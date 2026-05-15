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

from pathlib import Path

import cv2
import numpy as np
import pytesseract

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp"}
BASE_DIR = Path.cwd()
OUTPUT_DIR = BASE_DIR / "ocr_ready"


def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    if coords.size == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def preprocess_image(img_path):
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return deskew(cleaned)


def should_skip(path: Path):
    if OUTPUT_DIR in path.parents:
        return True
    return path.suffix.lower() not in SUPPORTED_EXT


def process():
    OUTPUT_DIR.mkdir(exist_ok=True)
    for path in BASE_DIR.rglob("*"):
        if should_skip(path):
            continue
        relative = path.relative_to(BASE_DIR)
        out_img_path = OUTPUT_DIR / relative
        out_txt_path = out_img_path.with_suffix(".txt")
        out_img_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Processing: {relative}")
        processed = preprocess_image(path)
        if processed is None:
            continue
        cv2.imwrite(str(out_img_path), processed)
        text = pytesseract.image_to_string(processed, config="--oem 1 --psm 6")
        Path(out_txt_path).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    process()
    print("Done. Images + OCR text saved in ./ocr_ready")
