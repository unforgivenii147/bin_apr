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

import os
import subprocess

from dh import get_ipkgs
from Pathlib import Path


def find_packages_with_bin_scripts(output_file="have_scripts.txt"):
    print("Starting search for packages with 'bin' scripts...")
    try:
        installed_packages = get_ipkgs()
        if not installed_packages:
            print("No Python packages found via 'pip list'. Please ensure pip is installed and accessible.")
            return
        print(f"Found {len(installed_packages)} installed packages. Checking each for 'bin' scripts...")
        packages_with_scripts = []
        total_packages = len(installed_packages)
        for i, package_name in enumerate(installed_packages):
            print(f"[{i + 1}/{total_packages}] Checking '{package_name}'...", end="\r")
            try:
                result = subprocess.run(
                    ["pip", "show", "-f", package_name],
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",
                    errors="ignore",
                )
                lines = result.stdout.split("\n")
                bin_indicators = [os.path.join(os.sep, "bin", ""), os.path.join("bin", ""), os.path.join("scripts", "")]
                found_script_in_bin = False
                for line in lines:
                    line = line.strip()
                    if line.startswith("Location:"):
                        continue
                    if line.startswith("Files:"):
                        continue
                    for indicator in bin_indicators:
                        if (
                            indicator in line.lower()
                            and (
                                line.endswith(".py")
                                or os.path.splitext(line)[1] == ""
                                or os.path.splitext(line)[1] == ".exe"
                            )
                            and (
                                not any(
                                    (
                                        exclude_part in line
                                        for exclude_part in ["__pycache__", ".dist-info", ".egg-info", ".pth"]
                                    )
                                )
                            )
                        ):
                            found_script_in_bin = True
                            break
                    if found_script_in_bin:
                        break
                if found_script_in_bin:
                    packages_with_scripts.append(package_name)
            except subprocess.CalledProcessError:
                pass
            except Exception as e:
                print(f"\nAn unexpected error occurred while checking '{package_name}': {e}")
        with Path(output_file).open("w", encoding="utf-8") as f:
            f.writelines((pkg + "\n" for pkg in packages_with_scripts))
        print(f"\nSearch complete. Found {len(packages_with_scripts)} packages with 'bin' scripts.")
        print(f"List saved to '{output_file}'.")
    except FileNotFoundError:
        print("Error: 'pip' command not found. Please ensure Python and pip are installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error running pip command: {e.cmd}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    find_packages_with_bin_scripts()
