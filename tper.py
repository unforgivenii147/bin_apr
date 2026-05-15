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

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

from deep_translator import GoogleTranslator
from tqdm import tqdm

INPUT_FILE = "words.txt"
OUTPUT_FILE = "dic.json"
MAX_WORKERS = 12
SAVE_EVERY = 1000
lock = Lock()


def translate_word(word):
    for attempt in range(3):
        try:
            return GoogleTranslator(source="auto", target="en").translate(word)
        except Exception as e:
            print(f"[WARN] Failed '{word}' (attempt {attempt + 1}): {e}")
            time.sleep(0.5)
    return None


def load_words(input_file):
    with Path(input_file).open(encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip()]


def load_existing_results(output_file):
    if Path(output_file).exists():
        try:
            with Path(output_file).open(encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[WARN] Could not load existing {output_file}: {e}")
    return {}


def save_results_atomic(results, output_file):
    tmp = output_file + ".tmp"
    with Path(tmp).open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    Path(tmp).replace(output_file)


def main():
    words = load_words(INPUT_FILE)
    print(f"[INFO] Loaded {len(words)} Persian words")
    results = load_existing_results(OUTPUT_FILE)
    print(f"[INFO] Loaded {len(results)} existing translations from {OUTPUT_FILE}")
    to_translate = [w for w in words if w not in results]
    total_remaining = len(to_translate)
    print(f"[INFO] {total_remaining} words to translate (will skip already translated)")
    if total_remaining == 0:
        print("[INFO] Nothing to do. Exiting.")
        return
    new_count = 0
    pbar = tqdm(total=total_remaining, desc="Translating", unit="word")
    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_map = {executor.submit(translate_word, w): w for w in to_translate}
            for future in as_completed(future_map):
                persian_word = future_map[future]
                try:
                    english = future.result()
                    with lock:
                        if english:
                            results[persian_word] = english
                            new_count += 1
                            print(f"{persian_word} → {english}")
                        else:
                            print(f"[FAIL] Could not translate: {persian_word}")
                        pbar.update(1)
                        if new_count % SAVE_EVERY == 0:
                            print(f"[INFO] Saving progress after {new_count} new translations...")
                            save_results_atomic(results, OUTPUT_FILE)
                except Exception as e:
                    print(f"[ERROR] Unexpected error for '{persian_word}': {e}")
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user. Saving progress...")
    finally:
        with lock:
            save_results_atomic(results, OUTPUT_FILE)
        pbar.close()
        print(f"\n[SAVED] Translation dictionary saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
