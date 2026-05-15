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

import os
import subprocess
import zipfile
from pathlib import Path


VENV_PATH = Path("~/venv").expanduser()


def get_installed_version(pkg_name):
    try:
        result = subprocess.run(
            [os.path.join(VENV_PATH, "bin", "pip"), "show", pkg_name], capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":")[1].strip()
    except Exception as e:
        print(f"Error checking installed version for {pkg_name}: {e}")
    return None


def get_wheel_package_info(wheel_file):
    try:
        with zipfile.ZipFile(wheel_file, "r") as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("METADATA"):
                    with zip_ref.open(file) as f:
                        metadata = f.read().decode("utf-8")
                        for line in metadata.splitlines():
                            if line.startswith("Name:"):
                                pkg_name = line.split(":")[1].strip()
                            if line.startswith("Version:"):
                                pkg_version = line.split(":")[1].strip()
                        return (pkg_name, pkg_version)
    except Exception as e:
        print(f"Error reading {wheel_file}: {e}")
    return (None, None)


def remove_wheel_file(wheel_file):
    try:
        Path(wheel_file).unlink()
        print(f"Removed: {wheel_file}")
    except Exception as e:
        print(f"Error removing {wheel_file}: {e}")


def main():
    whl_dir = "/sdcard/whl"
    if not Path(whl_dir).exists():
        print(f"Directory {whl_dir} does not exist.")
        return
    for file in os.listdir(whl_dir):
        if file.endswith(".whl"):
            wheel_file = os.path.join(whl_dir, file)
            pkg_name, pkg_version = get_wheel_package_info(wheel_file)
            if pkg_name and pkg_version:
                installed_version = get_installed_version(pkg_name)
                if installed_version:
                    if installed_version == pkg_version:
                        print(f"{pkg_name} {pkg_version} is already installed in the venv, removing {wheel_file}")
                        remove_wheel_file(wheel_file)
                    elif installed_version > pkg_version:
                        print(
                            f"{pkg_name} {installed_version} is newer than {pkg_version} in venv, removing {wheel_file}"
                        )
                        remove_wheel_file(wheel_file)
                    else:
                        print(
                            f"{pkg_name} {pkg_version} is newer than the installed version {installed_version} in venv. Keeping {wheel_file}"
                        )
                else:
                    print(f"{pkg_name} is not installed in the venv, keeping {wheel_file}")
            else:
                print(f"Could not extract info from {wheel_file}")


if __name__ == "__main__":
    main()
