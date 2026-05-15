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

import re
import sys
from pathlib import Path

from binaryornot import is_binary
from nltk.tokenize import sent_tokenize

DEFAULT_MAX = 5000
BINARY_SAMPLE = 4096


def split_long_by_words(segment: str, max_chars: int = DEFAULT_MAX):
    words = re.findall("\\S+\\s*", segment, flags=re.DOTALL)
    parts = []
    cur = ""
    for w in words:
        if len(cur) + len(w) <= max_chars:
            cur += w
        else:
            if cur:
                parts.append(cur)
            if len(w) > max_chars:
                i = 0
                while i < len(w):
                    slice_ = w[i : i + max_chars]
                    parts.append(slice_)
                    i += max_chars
                cur = ""
            else:
                cur = w
    if cur:
        parts.append(cur)
    return parts


def chunk_text_with_nltk(text: str, max_chars: int):
    sentences = sent_tokenize(text)
    chunks = []
    cur = ""
    for sent in sentences:
        sent_to_add = sent
        if cur and (not cur.endswith((" ", "\n"))) and (not sent_to_add.startswith((" ", "\n"))):
            sent_to_add = " " + sent_to_add
        if len(cur) + len(sent_to_add) <= max_chars:
            cur += sent_to_add
        else:
            if cur:
                chunks.append(cur)
                cur = ""
            if len(sent_to_add) <= max_chars:
                cur = sent_to_add
            else:
                parts = split_long_by_words(sent_to_add, max_chars)
                for p in parts[:-1]:
                    chunks.append(p)
                cur = parts[-1] if parts else ""
    if cur:
        chunks.append(cur)
    return chunks


def write_chunks(chunks, input_path: Path, out_dir: Path, encoding: str):
    stem = input_path.stem
    ext = "".join(input_path.suffixes)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, chunk in enumerate(chunks, start=1):
        out_name = f"{stem}_{i}{ext}"
        out_path = out_dir / out_name
        out_path.write_text(chunk, encoding=encoding)
        print(f"Wrote {out_path} ({len(chunk)} chars)")


def main():
    inp = Path(sys.argv[1])
    if not inp.exists() or not inp.is_file() or is_binary(inp):
        print(f"Input file not found or is binary: {inp.name}", file=sys.stderr)
        sys.exit(2)
    try:
        text = inp.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"Failed to read input file with encoding {args.encoding}: {exc}", file=sys.stderr)
        sys.exit(2)
    if len(text) < DEFAULT_MAX:
        print(f"File has fewer than {DEFAULT_MAX} characters ({len(text)}). Skipping.", file=sys.stderr)
        sys.exit(0)
    chunks = chunk_text_with_nltk(text, DEFAULT_MAX)
    if not chunks:
        print("No chunks produced. Exiting.", file=sys.stderr)
        sys.exit(0)
    out_dir = inp.parent
    write_chunks(chunks, inp, out_dir, "utf-8")
    print(f"Finished: {len(chunks)} files created")


if __name__ == "__main__":
    main()
