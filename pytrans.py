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
import time
from pathlib import Path

from deep_translator import GoogleTranslator
from tqdm import tqdm

MAX_CHARS = 5000


def get_output_filename(input_file):
    path = Path(input_file)
    stem = path.stem
    suffix = path.suffix
    return path.parent / f"{stem}_en{suffix}"


def load_file(input_file):
    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
    for encoding in encodings:
        try:
            with Path(input_file).open(encoding=encoding) as f:
                return f.read()
        except (OSError, UnicodeDecodeError):
            continue
    msg = f"Could not read file {input_file} with any encoding"
    raise OSError(msg)


def save_file(output_file, content):
    Path(output_file).write_text(content, encoding="utf-8")


def find_chunk_boundary(text, max_chars):
    if len(text) <= max_chars:
        return len(text)
    search_area = text[:max_chars]
    for delimiter in ["\n", "\r\n", ".  ", "!  ", "?  ", "; ", ", ", " "]:
        last_pos = search_area.rfind(delimiter)
        if last_pos > 0:
            return last_pos + len(delimiter)
    last_space = search_area.rfind(" ")
    if last_space > 0:
        return last_space + 1
    return max_chars


def chunk_text(text, max_chars):
    chunks = []
    pos = 0
    while pos < len(text):
        remaining = text[pos:]
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        chunk_end = find_chunk_boundary(remaining, max_chars)
        chunks.append(remaining[:chunk_end])
        pos += chunk_end
    return chunks


def translate_chunk(text, source_lang="auto"):
    for attempt in range(3):
        try:
            translator = GoogleTranslator(source=source_lang, target="en")
            translated = translator.translate(text)
            return (translated, source_lang)
        except Exception as e:
            print(f"[WARN] Translation failed (attempt {attempt + 1}/3): {e}")
            time.sleep(1 + attempt)
    msg = "Failed to translate chunk after 3 attempts"
    raise Exception(msg)


def translate_file(input_file, source_lang="auto"):
    print(f"[INFO] Reading file: {input_file}")
    content = load_file(input_file)
    content_length = len(content)
    print(f"[INFO] File size: {content_length} characters")
    if content_length <= MAX_CHARS:
        print(f"[INFO] Content fits in single request ({content_length} chars)")
        print("[INFO] Translating...")
        translated, detected_lang = translate_chunk(content, source_lang)
        print(f"[INFO] Detected language: {detected_lang}")
        return translated
    chunks = chunk_text(content, MAX_CHARS)
    total_chunks = len(chunks)
    print(f"[INFO] Content split into {total_chunks} chunks")
    print(f"[INFO] Chunk sizes: {[len(c) for c in chunks]}")
    translated_chunks = []
    detected_lang = None
    pbar = tqdm(total=total_chunks, desc="Translating", unit="chunk")
    try:
        for i, chunk in enumerate(chunks):
            print(f"\n[INFO] Translating chunk {i + 1}/{total_chunks} ({len(chunk)} chars)...")
            try:
                translated_chunk, detected_lang = translate_chunk(chunk, source_lang)
                translated_chunks.append(translated_chunk)
                pbar.update(1)
            except Exception as e:
                print(f"[ERROR] Failed to translate chunk {i + 1}: {e}")
                pbar.update(1)
                translated_chunks.append(chunk)
    finally:
        pbar.close()
    result = "".join(translated_chunks)
    print(f"\n[INFO] Detected language: {detected_lang}")
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage:  python translate_file.py <input_file> [source_language]")
        print("\nExamples:")
        print("  python translate_file.py document.txt")
        print("  python translate_file.py document. fa")
        print("  python translate_file.py document.txt fa")
        print("\nSupported languages:  auto, en, fa, fr, de, es, it, pt, ru, zh, ja, ko, ar, etc.")
        sys.exit(1)
    input_file = sys.argv[1]
    source_lang = sys.argv[2] if len(sys.argv) > 2 else "auto"
    if not Path(input_file).exists():
        print(f"[ERROR] File not found: {input_file}")
        sys.exit(1)
    output_file = get_output_filename(input_file)
    if Path(output_file).exists():
        print(f"[INFO] Output file already exists: {output_file}")
        print(f"[INFO] Skipping translation (delete {output_file} to re-translate)")
        sys.exit(0)
    print(f"[INFO] Input:   {input_file}")
    print(f"[INFO] Output: {output_file}")
    print(f"[INFO] Source language: {source_lang}")
    print()
    try:
        translated_content = translate_file(input_file, source_lang)
        print(f"\n[INFO] Saving result to: {output_file}")
        save_file(output_file, translated_content)
        print("\n[SUCCESS] Translation complete!")
        print(f"[INFO] Output file: {output_file}")
        print(f"[INFO] Output size: {len(translated_content)} characters")
    except Exception as e:
        print(f"\n[ERROR] Translation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
