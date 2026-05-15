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

import shlex
import stat
import sys
from hashlib import sha256
from pathlib import Path

from dh import expand_arg

CHUNK_SIZE = 32768


def get_sha256(path: str | Path) -> str:
    path = Path(path)
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def write_shell_copy(script_path: Path, src_root: Path, dst_root: Path, only_dirs, only_files):
    with script_path.open("w", encoding="utf-8") as sh:
        sh.write("#!/bin/sh\n")
        for d in sorted(only_dirs):
            dst_dir = dst_root / d
            sh.write(f"mkdir -p {shlex.quote(str(dst_dir))}\n")
        for f in sorted(only_files):
            dst_file = dst_root / f
            src_file = src_root / f
            parent = dst_file.parent
            sh.write(
                f"mkdir -p {shlex.quote(str(parent))} && cp -a {shlex.quote(str(src_file))} {shlex.quote(str(dst_file))}\n"
            )
    st = script_path.stat()
    script_path.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main():
    cwd = Path.cwd()
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    first = expand_arg(dir1)
    second = expand_arg(dir2)
    f_files = [p.name for p in first if p.is_file()]
    f_dirs = [p.name for p in first if p.is_dir()]
    s_files = [p.name for p in second if p.is_file()]
    s_dirs = [p.name for p in second if p.is_dir()]
    common1 = [Path(dir1).resolve() / p for p in f_files if p in s_files]
    common2 = {str(Path(dir1).resolve() / p): str(Path(dir2).resolve() / p) for p in f_files if p in s_files}
    if common1:
        for k in common1:
            print(f"  - {k}")
    else:
        print("no common files")
        sys.exit(1)
    only_files_first = [p for p in f_files if p not in s_files]
    only_files_second = [p for p in s_files if p not in f_files]
    common_txt = cwd / "common.txt"
    common_txt.write_text("\n".join([str(p) for p in common1]))
    ans = input(f"delete from {dir1}  ? ")
    if ans == "y":
        for k, v in common2.items():
            if get_sha256(k) == get_sha256(v):
                print(f"the files are identical \n{k}\n{v}")
            else:
                print(f"similar name filed:\n{k}\n{v}\n")


if __name__ == "__main__":
    main()
