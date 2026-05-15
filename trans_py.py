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

import ast
import os
import re
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from deep_translator import GoogleTranslator
from dh import DOC_TH1, DOC_TH2, get_pyfiles

PYTHON_EXT = ".py"
BACKUP_EXT = ".bak"
CHUNK_SIZE = 5000
TARGET_LANG = "en"
SRC_LANG = "auto"
_thread_local = threading.local()


def get_translator():
    if not hasattr(_thread_local, "translator"):
        _thread_local.translator = GoogleTranslator(source=SRC_LANG, target=TARGET_LANG)
    return _thread_local.translator


def is_non_english(line):
    return re.search("[^\\x00-\\x7F]", line)


def translate_line(line):
    if is_non_english(line.strip()):
        try:
            trans = get_translator().translate(line.strip())
            if trans and trans.strip() and (trans.strip() != line.strip()):
                return trans
        except Exception as e:
            print(f"Translation error: {e} -- Line: {line}")
            return None
    return None


def split_large_text_blocks(text, max_len):
    lines = text.splitlines(keepends=True)
    chunks = []
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) > max_len:
            chunks.append(chunk)
            chunk = ""
        chunk += line
    if chunk:
        chunks.append(chunk)
    return chunks


def translate_docstring(docstr):
    new_lines = []
    for line in docstr.splitlines():
        new_lines.append(line)
        transl = translate_line(line)
        if transl:
            new_lines.append(transl)
    return "\n".join(new_lines)


def process_file(filepath):
    backup_path = filepath + BACKUP_EXT
    shutil.copyfile(filepath, backup_path)
    code = Path(filepath).read_text(encoding="utf-8")
    len(code) > CHUNK_SIZE
    try:
        parsed = ast.parse(code, filename=filepath, type_comments=True)
    except Exception as e:
        print(f"Failed to parse {filepath}: {e}")
        return
    lines = code.splitlines(keepends=False)
    new_lines = list(lines)
    offset_map = {}
    for node in ast.walk(parsed):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            docstring = ast.get_docstring(node, clean=False)
            if docstring:
                doc_start = node.body[0].lineno - 1 if node.body else None
                for lookback in range(3):
                    possible = doc_start - lookback
                    if possible >= 0 and (
                        lines[possible].lstrip().startswith(DOC_TH1) or lines[possible].lstrip().startswith(DOC_TH2)
                    ):
                        docstring_line = possible
                        break
                else:
                    continue
                doc_lines = []
                line_idx = docstring_line
                quote_type = DOC_TH1 if lines[line_idx].lstrip().startswith(DOC_TH1) else DOC_TH2
                while True:
                    doc_lines.append(lines[line_idx])
                    if lines[line_idx].rstrip().endswith(quote_type) and line_idx != docstring_line:
                        break
                    line_idx += 1
                doc_block = "\n".join(doc_lines)
                doc_body = re.sub(f"^{quote_type}|{quote_type}$", "", doc_block.strip(), flags=re.MULTILINE).strip()
                translated_doc_body = translate_docstring(doc_body)
                translated_doc_block = f"{quote_type}\n{translated_doc_body}\n{quote_type}"
                start = docstring_line + offset_map.get(docstring_line, 0)
                end = line_idx + 1 + offset_map.get(line_idx, 0)
                translated_lines = translated_doc_block.splitlines()
                new_lines[start:end] = translated_lines
                offset = len(translated_lines) - (end - start)
                for k in range(end, len(new_lines)):
                    offset_map[k] = offset_map.get(k, 0) + offset
    final_lines = []
    for line in new_lines:
        final_lines.append(line)
        stripped = line.strip()
        if stripped.startswith("#") and is_non_english(stripped[1:]):
            trans = translate_line(stripped[1:].strip())
            if trans:
                indentation = re.match("\\s*", line).group(0)
                final_lines.append(f"{indentation}# {trans}")
    Path(filepath).write_text("\n".join(final_lines) + "\n", encoding="utf-8")
    print(f"Translated: {filepath}")


def main():
    cwd = Path.cwd()
    py_files = get_pyfiles(cwd)
    if not py_files:
        print("No Python files found.")
        return
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(process_file, f): f for f in py_files}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Failed processing {futures[future]}: {e}")


if __name__ == "__main__":
    main()
