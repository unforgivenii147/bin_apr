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
import sys
from pathlib import Path

import pytesseract
from deep_translator import GoogleTranslator
from langdetect import DetectorFactory, detect
from PIL import Image, ImageEnhance, ImageFilter

DetectorFactory.seed = 0
TEXT_EXT = {".txt", ".md", ".csv", ".json", ".py"}
IMAGE_EXT = {".jpg", ".jpeg", ".png"}
CHUNK_SIZE = 2000


def detect_lang_from_text(text: str) -> str:
    if not text.strip():
        return "unknown"
    try:
        return detect(text[:500])
    except Exception:
        return "unknown"


def read_text_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext not in TEXT_EXT:
        msg = f"Unsupported text file: {ext}"
        raise ValueError(msg)
    return path.read_text(encoding="utf-8")


def preprocess_image(img: Image.Image) -> Image.Image:
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = img.point(lambda x: 0 if x < 160 else 255)
    return img.filter(ImageFilter.MedianFilter(size=3))


def read_image_ocr(path: Path) -> str:
    try:
        img = Image.open(path)
        img = preprocess_image(img)
        return pytesseract.image_to_string(img)
    except Exception as e:
        msg = f"OCR failed: {e}"
        raise RuntimeError(msg)


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list:
    return [text[i : i + size] for i in range(0, len(text), size)]


def translate_chunks(chunks, src_lang: str) -> str:
    translator = GoogleTranslator(source=src_lang, target="en")
    output = [translator.translate(chunk) for chunk in chunks]
    return "".join(output)


def build_translated_output_path(input_path: Path) -> Path:
    if input_path.suffix.lower() in IMAGE_EXT:
        return input_path.with_name(f"{input_path.stem}_eng.txt")
    return input_path.with_name(f"{input_path.stem}_eng{input_path.suffix}")


def build_raw_ocr_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_ocr.txt")


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate text or image to English.")
    parser.add_argument("input_path")
    parser.add_argument("--lang", default="auto", help="Source language code or 'auto'")
    args = parser.parse_args()
    in_path = Path(args.input_path)
    if not in_path.exists():
        sys.exit(1)
    try:
        if in_path.suffix.lower() in TEXT_EXT:
            text = read_text_file(in_path)
        elif in_path.suffix.lower() in IMAGE_EXT:
            text = read_image_ocr(in_path)
            raw_ocr_path = build_raw_ocr_path(in_path)
            raw_ocr_path.write_text(text, encoding="utf-8")
        else:
            print("Unsupported file type. Use text, jpg, jpeg, png.")
            sys.exit(0)
    except Exception:
        sys.exit(1)
    src_lang = args.lang
    if src_lang == "auto":
        src_lang = detect_lang_from_text(text)
    src_lang = "vi"
    chunks = chunk_text(text)
    try:
        translated = translate_chunks(chunks, src_lang)
    except Exception:
        sys.exit(1)
    out_path = build_translated_output_path(in_path)
    try:
        out_path.write_text(translated, encoding="utf-8")
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
