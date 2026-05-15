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

import argparse
import mmap
import os
import re
import tokenize
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dh import get_pyfiles
from tqdm import tqdm

SIZE_THRESHOLD = 1 * 1024 * 1024
OLD_PRINT_RE = re.compile("(?m)^[ \\t]*print[ \\t]+[^(\\n]")


def _open_source(filepath: str):
    size = Path(filepath).stat().st_size
    f = Path(filepath).open("rb")
    if size > SIZE_THRESHOLD:
        return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    return f


def _read_text(filepath: str) -> str | None:
    try:
        with Path(filepath).open(encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def _has_rich_print_import(text: str) -> bool:
    return "from rich import print" in text


def regex_flag(filepath: str) -> bool:
    text = _read_text(filepath)
    if not text:
        return False
    if _has_rich_print_import(text):
        return False
    return bool(OLD_PRINT_RE.search(text))


def tokenizer_confirm(filepath: str) -> str | None:
    try:
        src = _open_source(filepath)
        tokens = list(tokenize.tokenize(src.readline))
    except Exception:
        return None
    for i, tok in enumerate(tokens):
        if tok.type == tokenize.NAME and tok.string == "print":
            line = tok.line.rstrip()
            if line.strip() == "print":
                continue
            j = i + 1
            while j < len(tokens) and tokens[j].type in {
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
            }:
                j += 1
            if j < len(tokens) and tokens[j].string != "(":
                return line
    return None


def autofix_file(filepath: str) -> bool:
    try:
        with Path(filepath).open(encoding="utf-8") as f:
            lines = f.readlines()
        if any((l.strip() == "from rich import print" for l in lines)):
            return False
        changed = False
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.rstrip() == "print":
                continue
            if stripped.startswith("print ") and (not stripped.startswith("print(")):
                indent = line[: len(line) - len(stripped)]
                content = stripped[len("print ") :].rstrip()
                lines[i] = f"{indent}print({content})\n"
                changed = True
        if changed:
            with Path(filepath).open("w", encoding="utf-8") as f:
                f.writelines(lines)
        return changed
    except Exception:
        return False


def process_file(filepath: str, autofix: bool) -> tuple[str, str] | None:
    if not regex_flag(filepath):
        return None
    confirmed = tokenizer_confirm(filepath)
    if not confirmed:
        return None
    if autofix:
        autofix_file(filepath)
    return (filepath, confirmed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Regex + tokenizer detection of Python 2 print")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("-a", "--autofix", action="store_true")
    parser.add_argument("-w", "--workers", type=int, default=os.cpu_count())
    args = parser.parse_args()
    py_files = get_pyfiles(args.path)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(process_file, f, args.autofix) for f in py_files]
        for future in tqdm(as_completed(futures), total=len(futures), desc="", unit="file"):
            result = future.result()
            if result:
                path, line = result
                print(f"{path}\n  {line}")


if __name__ == "__main__":
    main()
