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

import sys
from pathlib import Path

import tree_sitter_python as tsp
from dh import STDLIB, get_filez, get_installed_pkgs, is_binary
from termcolor import cprint
from tree_sitter import Language, Parser

parser = Parser()
parser.language = Language(tsp.language())
VALID = {"import_statement", "import_from_statement"}


def extract_file(src: bytes, tree):
    root = tree.root_node
    return [src[node.start_byte : node.end_byte].decode() for node in root.children if node.type in VALID]


def process_file(fp):
    src = fp.read_bytes()
    tree = parser.parse(src)
    return extract_file(src, tree)


def main():
    outfile = Path("importz.txt")
    all_imports = []
    seen = set()
    cwd = Path.cwd()
    allpyfiles = len(list(cwd.rglob("*.py")))
    cprint(f"{allpyfiles} python files found", "green")
    c = 0
    for f in get_filez(cwd):
        if is_binary(f):
            continue
        if f.suffix == ".py":
            cprint(f"{c}/{allpyfiles} {f.name}", "cyan")
            c += 1
            result = process_file(f)
            if result:
                for k in result:
                    if k not in seen:
                        seen.add(k)
                        all_imports.append(k)
    all_imports = sorted(all_imports)
    outfile.write_text("\n".join(all_imports), encoding="utf-8")
    content = outfile.read_text(encoding="utf-8")
    impoz = []
    for line in content.splitlines():
        line = line.lower()
        if line.startswith("import "):
            line = line.replace("import ", "")
            if " as " in line:
                indx = line.index(" as ")
                line = line[:indx]
            if "." in line:
                indx = line.index(".")
                line = line[:indx]
            if line not in impoz and (not line.startswith("_")):
                impoz.append(line + "\n")
        elif line.startswith("from "):
            line = line.replace("from ", "")
            if line.startswith("."):
                continue
            if " as " in line:
                indx = line.index(" as ")
                line = line[:indx]
            if "." in line:
                indx = line.index(".")
                line = line[:indx]
            if " import" in line:
                indx = line.index(" import")
                line = line[:indx]
            if line not in impoz and (not line.startswith("_")):
                impoz.append(line + "\n")
    impoz = sorted(set(impoz))
    stdlib_plus_installed = list(STDLIB)
    inpkg = [p.replace("-", "_").lower() for p in get_installed_pkgs()]
    stdlib_plus_installed.extend(inpkg)
    filterd = []
    for rq in impoz:
        if rq.strip() not in stdlib_plus_installed:
            print(rq.strip())
            filterd.append(rq)
    outfile.write_text("\n".join(filterd), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
