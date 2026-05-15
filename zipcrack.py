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

import multiprocessing as mp
import sys
import time
import zipfile
from pathlib import Path

from print_persian import print_persian as _print

'\ndef attempt_password2(args):\n    zip_file_path, password_candidate = args\n    try:\n        with AESZipFile(zip_file_path, "r") as zf:\n            zf.setpassword(password_candidate.encode("utf-8"))\n            zf.testzip()\n            return password_candidate\n    except RuntimeError as e:\n        if "Bad password" in str(e) or "Incorrect password" in str(e):\n            return None\n        _print(f"خطای ناشناخته در حین تلاش با \'{password_candidate}\': {e}")\n        return None\n    except Exception as e:\n        _print(f"خطای کلی در حین تلاش با \'{password_candidate}\': {e}")\n        return None\n'


def attempt_password(args):
    zip_file_path, password_candidate = args
    zip_file_path = Path(zip_file_path)
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zf:
            zf.testzip()
            return password_candidate
    except RuntimeError as e:
        if "Incorrect password" in str(e):
            return None
        return None
    except Exception as e:
        return None


def crack_zip_password_multiprocess(zip_file_path, password_list_path, extract_dir="extracted_files"):
    if not Path(zip_file_path).exists():
        return None
    if not Path(password_list_path).exists():
        return None
    try:
        with Path(password_list_path).open(encoding="utf-8", errors="ignore") as p_list:
            passwords = [p.strip() for p in p_list if p.strip()]
        total_passwords = len(passwords)
        start_time = time.time()
        tasks = [(zip_file_path, p) for p in passwords]
        num_processes = mp.cpu_count()
        with mp.Pool(num_processes) as pool:
            results = pool.imap_unordered(attempt_password, tasks, chunksize=100)
            found_password = None
            for i, result in enumerate(results):
                if result:
                    found_password = result
                    break
                (i + 1) % 1000 == 0 or i + 1 == total_passwords
            pool.terminate()
            pool.join()
        end_time = time.time()
        elapsed_time = end_time - start_time
        if found_password:
            try:
                Path(extract_dir).mkdir(exist_ok=True, parents=True)
                with zipfile.ZipFile(zip_file_path, "r") as zf_final:
                    zf_final.extractall(path=extract_dir, pwd=found_password.encode("utf-8"))
            except Exception as e:
                pass
            return found_password
        return None
    except Exception as e:
        return None


if __name__ == "__main__":
    zip_file = Path(sys.argv[1])
    pass_file = Path.home() / "isaac" / "wordlist.txt"
    found_password_mp = crack_zip_password_multiprocess(zip_file, pass_file)
    if found_password_mp:
        _print(f"\npassword: {found_password_mp}")
    else:
        _print("\nnot found.")
