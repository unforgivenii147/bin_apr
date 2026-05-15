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

import argparse
from os import scandir as _scandir
from pathlib import Path

from autoflake import fix_code as fix_with_autoflake
from autopep8 import fix_code as fix_with_autopep
from black import Mode as _Mode
from black import TargetVersion as _tv
from black import format_str
from dh import get_filez
from isort import code as fix_with_isort
from termcolor import cprint
from yapf.yapflib.yapf_api import FormatCode as fix_with_yapf

CHUNK_SIZE = 32768
SKIP_DIRS = {".git", "__pycache__", ".ruff_cache", ".pytest_cachr"}


def is_binary(path: Path | str) -> bool:
    path = Path(path)
    try:
        with path.open("rb") as f:
            chunk = f.read(CHUNK_SIZE)
        if not chunk:
            return False
        if b"\x00" in chunk:
            return True
        text_chars = bytearray(range(32, 127)) + b"\n\r\t\x08"
        nontext = sum((1 for b in chunk if b not in text_chars))
        return nontext / len(chunk) > 0.3
    except Exception:
        return True


def get_lines(fp):
    return [p.strip() for p in fp.read_text(encoding="utf-8").splitlines() if p.strip()]


def is_python_file(path: str | Path) -> bool:
    path = Path(path)
    if path.is_symlink():
        return False
    if path.suffix == ".py":
        return True
    if not path.suffix:
        lines = get_lines(path)
        if not lines:
            return False
        first_line = lines[0]
        if first_line.startswith("#!") and "python" in first_line:
            return True
        for line in lines:
            if line and (not line.startswith("#")):
                return line.startswith(("import ", "from ", "class ", "def "))
    return False


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


def gsz(path: str | Path) -> int:
    path = Path(path)
    total_size = 0
    if not path.exists():
        return 0
    if path.is_file():
        try:
            total_size = path.stat().st_size
        except OSError:
            return 0
    elif path.is_dir():
        for entry in _scandir(path):
            try:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += gsz(entry.path)
            except OSError:
                continue
    return total_size


def format_single_file(file_path, args) -> bool:
    before: int = gsz(file_path)
    after: int = before
    try:
        original_code: str = file_path.read_text(encoding="utf-8")
        if args.raui:
            code = fix_with_autoflake(original_code, remove_all_unused_imports=True)
            file_path.write_text(code, encoding="utf-8")
        if args.isort:
            code = fix_with_isort(original_code)
            file_path.write_text(code, encoding="utf-8")
        if args.black:
            code = format_str(original_code, mode=_Mode(target_versions={_tv.PY310, _tv.PY313}, line_length=120))
            file_path.write_text(code, encoding="utf-8")
        elif args.autopep:
            code = fix_with_autopep(original_code, options={"aggressive": 2})
            file_path.write_text(code, encoding="utf-8")
        else:
            code, _ = fix_with_yapf(original_code)
            file_path.write_text(code, encoding="utf-8")
        after = gsz(file_path)
        print(f"[OK] {file_path.name} ", end=" ")
        cprint(f"{fsz(before - after)}", "cyan")
        return False
    except Exception as e:
        cprint("[ERROR]", "red", end=" ")
        print(f"{file_path.name}: {e}")
        return False


def main() -> None:
    p = argparse.ArgumentParser(description="Fast Python API-based formatter (Lazy Loading)")
    p.add_argument("-b", "--black", action="store_true", help="Use black style")
    p.add_argument("-a", "--autopep", action="store_true", help="Use autopep8 style")
    p.add_argument("-i", "--isort", action="store_true", help="Sort imports")
    p.add_argument("-r", "--raui", action="store_true", help="Autoflake cleanup")
    args = p.parse_args()
    cwd = Path.cwd()
    before = gsz(cwd)
    for f in get_filez(cwd):
        if is_binary(f):
            continue
        if is_python_file(f):
            format_single_file(f, args)
    diffsize = before - gsz(cwd)
    cprint(f"{fsz(diffsize)}", "cyan")


if __name__ == "__main__":
    main()
