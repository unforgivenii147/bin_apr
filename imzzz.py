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
import multiprocessing as mp
import os
import tarfile
import zipfile
from pathlib import Path

from dh import PKG_MAPPING, STDLIB

STD_LIB = STDLIB
MAPPING = PKG_MAPPING
try:
    with Path("/sdcard/pip.txt").open("r", encoding="utf-8") as f:
        PIP_PACKAGES = {line.strip().split("==")[0].split("[")[0] for line in f if line.strip()}
except FileNotFoundError:
    PIP_PACKAGES = set()


def is_python_file(file_path):
    return file_path.suffix == ".py" or (
        not file_path.suffix
        and any(
            (
                line.startswith(("import ", "from ", "#!/usr/bin/env python"))
                for line in Path(file_path).open(encoding="utf-8", errors="ignore")
            )
        )
    )


def extract_compressed(file_path, extract_to) -> None:
    if file_path.suffix == ".zip":
        with zipfile.ZipFile(file_path, "r") as z:
            z.extractall(extract_to)
    elif file_path.suffix in {".tar.gz", ".tar.xz", ".tar.zst"}:
        with tarfile.open(file_path, "r:*") as tar:
            tar.extractall(extract_to)
    elif file_path.suffix == ".whl":
        with zipfile.ZipFile(file_path, "r") as z:
            z.extractall(extract_to)


def get_imports(file_path):
    imports = set()
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split(".")[0]
                if (
                    module not in STD_LIB
                    and (not module.startswith("."))
                    and (not file_path.parent.match(f"*{module}*"))
                ):
                    imports.add(MAPPING.get(module, module))
        elif isinstance(node, ast.ImportFrom):
            module = node.module.split(".")[0] if node.module else ""
            if (
                module
                and module not in STD_LIB
                and (not module.startswith("."))
                and (not file_path.parent.match(f"*{module}*"))
            ):
                imports.add(MAPPING.get(module, module))
    return imports


def process_file(file_path):
    if file_path.is_dir():
        return set()
    if file_path.suffix in {".zip", ".whl", ".tar.gz", ".tar.xz", ".tar.zst"}:
        extract_dir = file_path.parent / f"extracted_{file_path.stem}"
        extract_compressed(file_path, extract_dir)
        imports = set()
        for root, _, files in os.walk(extract_dir):
            for f in files:
                f_path = Path(root) / f
                if is_python_file(f_path):
                    imports.update(get_imports(f_path))
        return imports
    if is_python_file(file_path):
        return get_imports(file_path)
    return set()


def main() -> None:
    root = Path()
    python_files = []
    for ext in ("*.py", "*"):
        python_files.extend(root.rglob(ext))
    with mp.Pool() as pool:
        results = pool.map(process_file, python_files)
    all_imports = set().union(*results)
    requirements = sorted(all_imports & PIP_PACKAGES)
    with Path("requirements.txt").open("w", encoding="utf-8") as f:
        f.writelines((f"{req}\n" for req in requirements))


if __name__ == "__main__":
    main()
