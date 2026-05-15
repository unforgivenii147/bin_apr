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

import ast
import importlib
import inspect
import os
import sys
from collections import deque
from multiprocessing import get_context
from pathlib import Path
from textwrap import dedent

from dh import get_files, unique_path

cwd = Path.cwd()
cwdname = cwd.name
BASE_DIR = Path(f"{cwdname}_doc")


def format_markdown(module_name: str, module_doc: str, functions, classes) -> str:
    parts = [f"# Module `{module_name}`\n"]
    if module_doc:
        parts.extend(("## Module Doc\n", module_doc + "\n"))
    if functions:
        parts.append("## Functions\n")
        for name, doc in functions:
            parts.extend((f"### `{name}()`\n", doc + "\n"))
    if classes:
        parts.append("## Classes\n")
        for name, doc in classes:
            parts.extend((f"### `{name}`\n", doc + "\n"))
    return "\n".join(parts).strip() + "\n"


def extract_ast_docs(src: str) -> tuple[str, list, list]:
    try:
        tree = ast.parse(src)
    except Exception:
        return ("", [], [])
    module_doc = dedent(ast.get_docstring(tree) or "").strip()
    functions = []
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node) or ""
            doc = dedent(doc).strip()
            if doc:
                functions.append((node.name, doc))
        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node) or ""
            doc = dedent(doc).strip()
            if doc:
                classes.append((node.name, doc))
    return (module_doc, functions, classes)


def extract_from_file(py_path: str) -> tuple[str, str, str, list, list]:
    try:
        src = Path(py_path).read_text(encoding="utf-8")
    except Exception:
        return None
    module_doc, functions, classes = extract_ast_docs(src)
    if not module_doc and (not functions) and (not classes):
        return None
    return (module_doc, functions, classes)


def extract_from_importable(name: str):
    try:
        module = importlib.import_module(name)
    except Exception:
        return None
    try:
        src = inspect.getsource(module)
        return extract_ast_docs(src)
    except Exception:
        doc = dedent(inspect.getdoc(module) or "").strip()
        if not doc:
            return None
        return (doc, [], [])


def module_to_md_paths(name: str):
    parts = name.split(".")
    folder = os.path.join(BASE_DIR, *parts[:-1])
    filename = f"{parts[-1]}.md"
    return (folder, os.path.join(folder, filename))


def file_to_md_paths(py_file: str, root: str):
    rel = os.path.relpath(py_file, root)
    parts = rel.split(os.sep)
    parts[-1] = parts[-1].replace(".py", ".md")
    folder = os.path.join(BASE_DIR, *parts[:-1])
    outfile = os.path.join(BASE_DIR, *parts)
    return (folder, outfile)


def save_markdown(folder: str, path: str, content: str):
    folderpath = Path(folder)
    if not folderpath.exists():
        folderpath.mkdir(exist_ok=True)
    outpath = Path(path)
    if outpath.exists():
        outpath = unique_path(outpath)
    outpath.write_text(content, encoding="utf-8")


def process_importable_task(name: str):
    print(f"processing module {name}")
    result = extract_from_importable(name)
    if not result:
        return
    module_doc, functions, classes = result
    folder, out_path = module_to_md_paths(name)
    md = format_markdown(name, module_doc, functions, classes)
    save_markdown(folder, out_path, md)


def process_file_task(py_file):
    filepath = Path(py_file)
    root = str(filepath.parent)
    print(f"processing file {filepath.name} from {filepath.parent.name}")
    result = extract_from_file(str(py_file))
    if not result:
        return
    module_doc, functions, classes = result
    rel = os.path.relpath(py_file)
    module_name = rel.replace(os.sep, ".").replace(".py", "")
    folder, out_path = file_to_md_paths(py_file, root)
    md = format_markdown(module_name, module_doc, functions, classes)
    save_markdown(folder, out_path, md)


def main():
    if not BASE_DIR.exists():
        BASE_DIR.mkdir(exist_ok=True)
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(cwd, extensions=[".py", ".pyi", ".pyx", ".pxd"])
    print(f"processing {len(files)} files")
    with get_context("spawn").Pool(4) as pool:
        pending = deque()
        for f in files:
            pending.append(pool.apply_async(process_file_task, (f,)))
            if len(pending) > 8:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


"\n    print(f\"processing {len(importable)} importable\")\n    with get_context('spawn').Pool(8) as pool:\n        pending=deque()\n        for x in importables:\n            pending.append(pool.apply_async(process_importable_task, (x,)))\n            if len(pending)>16:\n                pending.popleft().get()\n        while pending:\n            pending.popleft().get()\n"
if __name__ == "__main__":
    main()
