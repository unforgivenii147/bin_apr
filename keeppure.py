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

import csv
import os
import site
from multiprocessing import cpu_count
from pathlib import Path


def get_all_dist_info_dirs():
    dist_info_dirs = []
    for site_dir in [*site.getsitepackages(), site.getusersitepackages()]:
        if Path(site_dir).exists():
            dist_info_dirs.extend(
                (os.path.join(site_dir, item) for item in os.listdir(site_dir) if item.endswith(".dist-info"))
            )
    return dist_info_dirs


def check_package_binary(dist_info_path):
    record_file = os.path.join(dist_info_path, "RECORD")
    pkg_name = Path(dist_info_path).name.replace(".dist-info", "").split("-")[0].lower()
    if Path(record_file).exists():
        try:
            with Path(record_file).open(encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and any((row[0].endswith(ext) for ext in [".so", ".pyd"])):
                        return pkg_name
        except:
            pass
    return None


def get_binary_packages_parallel():
    dist_info_dirs = get_all_dist_info_dirs()
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(check_package_binary, dist_info_dirs)
    return {pkg for pkg in results if pkg}


def clean_requirements_txt(requirements_file="requirements.txt"):
    if not Path(requirements_file).exists():
        print(f"Error: {requirements_file} not found")
        return
    binary_packages = get_binary_packages_parallel()
    with Path("/sdcard/data/binary").open("w", encoding="utf-8") as fbin:
        fbin.write("\n".join(binary_packages))
        print("binary_pkgs created.")
    with Path(requirements_file).open(encoding="utf-8") as f:
        lines = [line.rstrip() for line in f]
    comments = [line for line in lines if line.startswith("#")]
    requirements = [line for line in lines if line and (not line.startswith("#"))]
    pure_python = []
    removed = []
    for req in requirements:
        pkg_name = req.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip().lower()
        if pkg_name in binary_packages:
            removed.append(req)
        else:
            pure_python.append(req)
    with Path(requirements_file).open("w", encoding="utf-8") as f:
        f.writelines((f"{comment}\n" for comment in comments))
        f.writelines((f"{pkg}\n" for pkg in sorted(pure_python)))
    if removed:
        print(f"\n🗑️  Removed binary packages ({len(removed)}):")
        for pkg in sorted(removed):
            print(f"   - {pkg}")
    else:
        print("✅ No binary packages found in requirements.txt")


if __name__ == "__main__":
    import sys

    req_file = sys.argv[1] if len(sys.argv) > 1 else "requirements.txt"
    clean_requirements_txt(req_file)
