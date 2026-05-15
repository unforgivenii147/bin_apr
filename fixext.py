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
import sys
from pathlib import Path

from dh import MIME2EXT, cprint, is_binary, unique_path

CONFIRM = False


def fix_by_shebang(fp) -> bool:
    if is_binary(fp) or not fp.stat().st_size:
        return False
    content = fp.read_text(encoding="utf8")
    fl = content.splitlines()[0]
    if fl.startswith("#!") and ("bash" in fl or "/bin/sh" in fl):
        new_path = fp.with_suffix(".sh")
        if new_path.exists():
            new_path = unique_path(new_path)
        fp.rename(new_path)
        return True
    elif fl.startswith("#!") and "python" in fl:
        new_path = fp.with_suffix(".py")
        if new_path.exists():
            new_path = unique_path(new_path)
        fp.rename(new_path)
        return True
    elif fl.startswith("#!") and "perl" in fl:
        new_path = fp.with_suffix(".pl")
        if new_path.exists():
            new_path = unique_path(new_path)
        print(f"rename {fp.name} -> {new_path.name}")
        ans = input("?")
        if ans == "y":
            fp.rename(new_path)
            return True
        return False
    elif fl.startswith("#!") and "node" in fl:
        new_path = fp.with_suffix(".js")
        if new_path.exists():
            new_path = unique_path(new_path)
        print(f"rename {fp.name} -> {new_path.name}")
        ans = input("?")
        if ans == "y":
            fp.rename(new_path)
            return True
        return False
    else:
        return False
    return False


def get_file_mime(path):
    try:
        result = subprocess.run(["file", "--brief", "--mime-type", path], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error detecting file type for {path}: {e}", file=sys.stderr)
        return None


def safe_rename(old_path, new_path):
    base, ext = os.path.splitext(new_path)
    counter = 1
    while Path(new_path).exists():
        new_path = f"{base}_{counter}{ext}"
        counter += 1
    cprint(f"{old_path} -> {new_path} ?")
    Path(old_path).rename(new_path)
    return new_path


def check_files(directory):
    mismatched_files = []
    for root, _, files in os.walk(directory):
        for name in files:
            path = Path(root) / name
            if ".git" in path.parts or "__pycache__" in path.parts:
                continue
            ext = path.suffix.lower()
            if fix_by_shebang(path):
                continue

            if ext in {".svg", ".c", ".py", ".js", ".css", ".ts", ".map", ".jsx", ".tsx", ".mjs", ".mts"}:
                continue

            mime = get_file_mime(path)
            print(f"{name} --> {mime}")

            if mime:
                expected_exts = MIME2EXT.get(mime, [])
                if expected_exts and ext not in expected_exts:
                    new_path = None
                    new_ext = expected_exts[0]
                    new_name = os.path.splitext(name)[0] + new_ext
                    new_path = Path(root) / new_name
                    if new_name == name:
                        continue
                    if new_path.exists():
                        new_path = unique_path(new_path)
                    if CONFIRM:
                        print(f"{path.name} -> {new_path.name}")
                        ans = input()
                        if ans == "y":
                            path.rename(new_path)
                    else:
                        path.rename(new_path)
                    mismatched_files.append((path, ext, mime, new_path))
    return mismatched_files


def main():
    cwd = Path.cwd()
    mismatches = check_files(cwd)
    if mismatches:
        print("Files with mismatched extensions:")
        for path, _ext, mime, new_path in mismatches:
            if new_path:
                print(f"\x1b[5;93m{path.name} {mime} \x1b[5;96m{new_path.name}]\x1b[0m")
            else:
                print(f"{path.name} -> \x1b[5m;94mdetected: {mime}\x1b[0m")
    else:
        cprint("no mismatch")


if __name__ == "__main__":
    main()
