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
import subprocess
import sys
from multiprocessing import cpu_count
from pathlib import Path


def convert_html_to_md(html_file: Path, executable: str = "html2md") -> tuple[Path, bool]:
    if html_file.suffix.lower() in {".html", ".htm"}:
        md_file = html_file.with_suffix(".md")
    else:
        print(f"Warning: {html_file} doesn't have .html/.htm extension, skipping.")
        return (html_file, False)
    try:
        result = subprocess.run([executable, str(html_file)], capture_output=True, text=True, check=True)
        md_file.write_text(result.stdout, encoding="utf-8")
        print(f"✓ Converted: {html_file} -> {md_file}")
        return (md_file, True)
    except subprocess.CalledProcessError as e:
        print(f"✗ Error converting {html_file}: {e.stderr}", file=sys.stderr)
        return (html_file, False)
    except FileNotFoundError:
        print(f"✗ Error: '{executable}' executable not found. Make sure it's in your PATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error converting {html_file}: {e}", file=sys.stderr)
        return (html_file, False)


def find_html_files(directory: Path, recursive: bool = True) -> list[Path]:
    if recursive:
        html_files = list(directory.rglob("*.html")) + list(directory.rglob("*.htm"))
    else:
        html_files = list(directory.glob("*.html")) + list(directory.glob("*.htm"))
    return sorted(html_files)


def process_file_wrapper(args: tuple) -> tuple[Path, bool]:
    html_file, executable = args
    return convert_html_to_md(html_file, executable)


def main():
    parser = argparse.ArgumentParser(
        description="Convert HTML files to Markdown using html2md executable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\nExamples:\n  %(prog)s\n  %(prog)s -r\n  %(prog)s file.html\n  %(prog)s /path/to/directory\n  %(prog)s /path/to/dir --no-recursive\n        ",
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="HTML file or directory to process (default: current directory)"
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", default=True, help="Process directories recursively (default: True)"
    )
    parser.add_argument("--no-recursive", action="store_false", dest="recursive", help="Disable recursive processing")
    parser.add_argument("--executable", default="html2md", help="Path to html2md executable (default: html2md)")
    parser.add_argument(
        "--workers", type=int, default=cpu_count(), help=f"Number of worker processes (default: {cpu_count()})"
    )
    args = parser.parse_args()
    input_path = Path(args.path).resolve()
    if not input_path.exists():
        print(f"Error: Path '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if input_path.is_file():
        html_files = [input_path]
    elif input_path.is_dir():
        html_files = find_html_files(input_path, args.recursive)
        if not html_files:
            print(f"No HTML files found in {input_path}")
            sys.exit(0)
        print(f"Found {len(html_files)} HTML file(s) to process")
    else:
        print(f"Error: '{input_path}' is neither a file nor a directory.", file=sys.stderr)
        sys.exit(1)
    if len(html_files) == 1:
        convert_html_to_md(html_files[0], args.executable)
    else:
        print(f"Using {args.workers} worker process(es)")
        process_args = [(f, args.executable) for f in html_files]
        with Pool(processes=args.workers) as pool:
            results = pool.map(process_file_wrapper, process_args)
        successful = sum((1 for _, success in results if success))
        print(f"\n{'=' * 50}")
        print(f"Conversion complete: {successful}/{len(html_files)} files converted successfully")


if __name__ == "__main__":
    main()
