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

import ast
import io
import re
import shutil
import tempfile
import tokenize
from multiprocessing import get_context
from pathlib import Path

from deep_translator import GoogleTranslator
from dh import DOC_TH1, DOC_TH2
from fastwalk import walk_files

DIRECTORY = "."
non_english_pattern = re.compile("[^\\x00-\\x7F]")


def is_english(text: str) -> bool:
    return not non_english_pattern.search(text)


def chunk_text(text: str, size: int = 800) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


def translate_chunk(chunk: str) -> str:
    try:
        result = GoogleTranslator(source="auto", target="en").translate(chunk)
        return result or chunk
    except Exception as e:
        print(f"  Translation error for chunk: {e}")
        return chunk


def translate_text(text: str) -> str:
    chunks = chunk_text(text)
    with get_context("spawn").Pool(8) as pool:
        translated = list(pool.imap(translate_chunk, chunks))
    return "".join(translated)


def safe_overwrite(filepath: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, dir=filepath.parent) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    shutil.move(tmp_path, filepath)


def extract_docstrings(tree: ast.AST) -> dict[int, str]:
    docstrings = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc and (not is_english(doc)):
                docstrings[id(node)] = doc
    return docstrings


def translate_python_file(source: str) -> str:
    print("  Analyzing Python structure...")
    tree = ast.parse(source)
    docstrings = extract_docstrings(tree)
    if docstrings:
        print(f"  Found {len(docstrings)} non-English docstrings")
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    result = []
    prev_end = (1, 0)
    translated_count = 0
    for i, token in enumerate(tokens):
        tok_type, tok_str, start, end, _line = token
        if start > prev_end:
            lines_between = source.splitlines()[prev_end[0] - 1 : start[0]]
            if len(lines_between) > 1:
                result.extend((line_content + "\n" for line_content in lines_between[:-1]))
                result.append(lines_between[-1][: start[1]])
            elif lines_between:
                result.append(lines_between[0][prev_end[1] : start[1]])
        if tok_type == tokenize.COMMENT and (not is_english(tok_str)):
            comment_text = tok_str[1:].strip()
            print(f"  Translating comment: {comment_text[:50]}...")
            translated = translate_text(comment_text)
            result.append(f"# {translated}")
            translated_count += 1
        elif tok_type == tokenize.STRING:
            stripped = tok_str.strip("'\"")
            if stripped and (not is_english(stripped)) and (len(stripped) > 10):
                try:
                    print(f"  Translating string: {stripped[:50]}...")
                    translated = translate_text(stripped)
                    if tok_str.startswith((DOC_TH1, DOC_TH2)):
                        quote_char = tok_str[:3]
                        tok_str = f"{quote_char}{translated}{quote_char}"
                    else:
                        quote_char = tok_str[0]
                        tok_str = f"{quote_char}{translated}{quote_char}"
                    translated_count += 1
                except Exception as e:
                    print(f"  Error translating string: {e}")
            result.append(tok_str)
        else:
            result.append(tok_str)
        prev_end = end
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1} tokens...")
    print(f"  Translated {translated_count} items")
    return "".join(result)


def process_files(directory: str) -> None:
    print(f"Scanning directory: {directory}")
    paths = [Path(p) for p in walk_files(directory)]
    files = [p for p in paths if p.is_file()]
    supported_extensions = {".txt", ".md", ".srt", ".json", ".html", ".py"}
    target_files = [f for f in files if f.suffix.lower() in supported_extensions]
    print(f"Found {len(target_files)} supported files out of {len(files)} total files")
    print("-" * 50)
    translated_count = 0
    skipped_count = 0
    error_count = 0
    for i, fp in enumerate(target_files, 1):
        suffix = fp.suffix.lower()
        print(f"[{i}/{len(target_files)}] Processing: {fp}")
        try:
            original = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  Error reading file: {e}")
            error_count += 1
            continue
        if is_english(original.strip()):
            print("  File is already in English, skipping")
            skipped_count += 1
            continue
        print("  Translating content...")
        try:
            translated = translate_python_file(original, fp) if suffix == ".py" else translate_text(original)
            if translated.strip() != original.strip():
                safe_overwrite(fp, translated)
                print("  ✓ Successfully translated and saved")
                translated_count += 1
            else:
                print("  Translation produced same content, skipping")
                skipped_count += 1
        except Exception as e:
            print(f"  ✗ Error processing file: {e}")
            error_count += 1
        print("-" * 30)
    print("TRANSLATION SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {len(target_files)}")
    print(f"Successfully translated: {translated_count}")
    print(f"Skipped (already English): {skipped_count}")
    print(f"Errors: {error_count}")
    print("=" * 50)


if __name__ == "__main__":
    process_files(DIRECTORY)
