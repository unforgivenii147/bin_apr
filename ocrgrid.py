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

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image


def pil_to_cv(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def cv_to_pil(img: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def to_grayscale(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def rescale(img: np.ndarray, scale: float = 2.0) -> np.ndarray:
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)


def deskew(img: np.ndarray) -> np.ndarray:
    gray = to_grayscale(img)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def rotate(img: np.ndarray, angle: int) -> np.ndarray:
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_CUBIC)


def run_tesseract(img: Image.Image, psm: int, oem: int, dpi: int) -> dict[str, str]:
    config = f"--psm {psm} --oem {oem} -c user_defined_dpi={dpi}"
    text = pytesseract.image_to_string(img, config=config)
    return {"psm": psm, "oem": oem, "dpi": dpi, "config": config, "text": text}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", type=Path)
    parser.add_argument("-o", "--out", type=Path, default=Path("ocr_output"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    base_img = Image.open(args.fname).convert("RGB")
    cv_img = pil_to_cv(base_img)
    image_variants: dict[str, Image.Image] = {
        "original": base_img,
        "grayscale": cv_to_pil(to_grayscale(cv_img)),
        "rescaled": cv_to_pil(rescale(cv_img)),
        "deskewed": cv_to_pil(deskew(cv_img)),
        "rotated_90": cv_to_pil(rotate(cv_img, 90)),
    }
    psm_values = [3, 4, 6, 11]
    oem_values = [1, 3]
    dpi_values = [150, 300]
    report_index: list[dict] = []
    for variant_name, img in image_variants.items():
        variant_dir = args.out / variant_name
        variant_dir.mkdir(exist_ok=True)
        for psm in psm_values:
            for oem in oem_values:
                for dpi in dpi_values:
                    result = run_tesseract(img, psm, oem, dpi)
                    tag = f"psm{psm}_oem{oem}_dpi{dpi}"
                    txt_path = variant_dir / f"{tag}.txt"
                    meta_path = variant_dir / f"{tag}.json"
                    txt_path.write_text(result["text"], encoding="utf-8")
                    meta_path.write_text(
                        json.dumps(
                            {"image_variant": variant_name, "source_file": str(args.fname), "tesseract": result},
                            indent=2,
                        ),
                        encoding="utf-8",
                    )
                    report_index.append(
                        {"variant": variant_name, "psm": psm, "oem": oem, "dpi": dpi, "text_file": str(txt_path)}
                    )
    (args.out / "index.json").write_text(json.dumps(report_index, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
