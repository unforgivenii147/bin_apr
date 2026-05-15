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
import hashlib
import logging
import operator
import shutil
from pathlib import Path
from dh import get_pyfiles
from joblib import Parallel, delayed

OUTPUT_DIR = Path.home() / "isaac" / "may" / "pkgs" / "dh2" / "src" / "dh2" / "output"
OUTPUT_FILE = OUTPUT_DIR / "const.py"
LOG_FILE = OUTPUT_DIR / "error.log"
OUTPUT_DIR.mkdir(exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


def get_file_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with Path(filepath).open("rb") as f:
        while chunk := f.read(32768):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_constants(filepath: Path) -> list[tuple[str, str, str]]:
    constants = []
    try:
        with Path(filepath).open("r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                is_simple_assign = all((isinstance(t, ast.Name) for t in node.targets))
                if is_simple_assign and isinstance(node.value, ast.Constant):
                    for target in node.targets:
                        const_name = target.id
                        if const_name.isupper():
                            const_value = ast.unparse(node.value)
                            const_type = type(node.value.value).__name__
                            constants.append((const_name, const_value, const_type))
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.value is not None:
                    if node.target.id.isupper():
                        const_name = node.target.id
                        const_value = ast.unparse(node.value)
                        const_type = (
                            type(node.value.value).__name__ if isinstance(node.value, ast.Constant) else "unknown"
                        )
                        constants.append((const_name, const_value, const_type))
    except SyntaxError as e:
        logging.error(f"Syntax error in {filepath}: {e}")
    except Exception as e:
        logging.error(f"Error processing {filepath}: {e}")
    return constants


def process_file(filepath: Path) -> tuple[str, list[tuple[str, str, str]] | None]:
    file_hash = get_file_hash(filepath)
    constants = extract_constants(filepath)
    return (file_hash, constants)


def main():
    #    OUTPUT_DIR.mkdir(exist_ok=True)
    cwd = Path.cwd()
    python_files = list(get_pyfiles(cwd))
    if not python_files:
        print("No Python files found in the current directory.")
        return
    print(f"Found {len(python_files)} Python files. Processing...")
    results = Parallel(n_jobs=-1)((delayed(process_file)(f) for f in python_files))
    unique_constants = {}
    processed_hashes = set()
    all_constants_by_hash = {}
    for file_hash, constants in results:
        if constants is None:
            continue
        if file_hash not in processed_hashes:
            processed_hashes.add(file_hash)
            for name, value, ctype in constants:
                if file_hash not in all_constants_by_hash:
                    all_constants_by_hash[file_hash] = []
                constant_repr = f"{name} = {value}"
                found = False
                for idx, (existing_name, existing_value, _existing_type) in enumerate(all_constants_by_hash[file_hash]):
                    if existing_name == name and existing_value == value:
                        all_constants_by_hash[file_hash][idx] = (name, value, ctype)
                        found = True
                        break
                if not found:
                    all_constants_by_hash[file_hash].append((name, value, ctype))
    final_constants = []
    for file_hash, const_list in all_constants_by_hash.items():
        final_constants.extend(const_list)
    final_constants.sort(key=operator.itemgetter(0))
    with Path(OUTPUT_FILE).open("w", encoding="utf-8") as f:
        f.write("# Automatically generated constants file\n")
        f.write("# Based on files in the current directory\n\n")
        written_consts = set()
        for name, value, ctype in final_constants:
            constant_line = f"{name} = {value}"
            if constant_line not in written_consts:
                f.write(f"# Type: {ctype}\n")
                f.write(f"{constant_line}\n\n")
                written_consts.add(constant_line)
    print(f"Successfully extracted {len(written_consts)} unique constants to {OUTPUT_FILE}")
    if LOG_FILE.exists():
        print(f"Errors logged to {LOG_FILE}")


if __name__ == "__main__":
    main()
