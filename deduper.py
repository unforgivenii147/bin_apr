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
import ast
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

CURRENT_DIR = Path(".")
UTILS_FILE = CURRENT_DIR / "utils.py"
TOP_LEVEL_NODES = (ast.FunctionDef, ast.ClassDef, ast.Assign)
CONSTANT_NODES = (ast.Assign,)


def is_simple_constant(node: ast.Assign) -> bool:
    if len(node.targets) != 1:
        return False
    target = node.targets[0]
    if not isinstance(target, ast.Name):
        return False
    value = node.value
    if isinstance(value, ast.Constant):
        return True
    elif isinstance(value, ast.Name):
        return True
    elif isinstance(value, ast.UnaryOp) and isinstance(value.operand, (ast.Constant, ast.Name)):
        return True
    return False


def get_name(node: ast.AST) -> str:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        return node.name
    elif isinstance(node, ast.Assign):
        if len(node.targets) > 0 and isinstance(node.targets[0], ast.Name):
            return node.targets[0].id
        elif isinstance(node.targets[0], (ast.Tuple, ast.List)):
            return ""
    return ""


def node_to_source(node: ast.AST, source_lines: List[str]) -> str:
    start_line = node.lineno - 1
    end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start_line + 1
    if end_line <= start_line:
        end_line = start_line + 1
    return "\n".join(source_lines[start_line:end_line])


def hash_node(node: ast.AST, source_lines: List[str]) -> str:
    src = node_to_source(node, source_lines)
    normalized = "\n".join((line.rstrip() for line in src.splitlines())).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def collect_definitions(file_path: Path) -> List[Tuple[str, str, ast.AST]]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        try:
            _ = ast.parse(source)
        except:
            print(f"{file_path} ast parse error")
            sys.exit(1)
        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        print(f"[WARN] Syntax error in {file_path}: {e}")
        return []
    definitions = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            name = node.name
            h = hash_node(node, source_lines)
            definitions.append((name, h, node))
        elif isinstance(node, ast.Assign) and is_simple_constant(node):
            name = get_name(node)
            if name:
                h = hash_node(node, source_lines)
                definitions.append((name, h, node))
    return definitions


def ensure_utils_file():
    if UTIL_FILE.exists():
        print("utils.py exists. overwrite?")
        ans = input()
        if ans != "y":
            sys.exit(0)
    if not UTILS_FILE.exists():
        UTILS_FILE.write_text("# Auto-generated utilities from deduplication\n\n")
        return True
    content = UTILS_FILE.read_text()
    if "# Auto-generated" not in content:
        UTILS_FILE.write_text("# Auto-generated utilities from deduplication\n\n" + content)
    return False


def get_imports_from_file(file_path: Path) -> List[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return []
    imports = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            imports.append(line.rstrip())
    return imports


def add_import_to_file(file_path: Path, new_import: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith("#!"):
            insert_pos = i + 1
        elif line.startswith("# -*- coding:"):
            insert_pos = i + 1
        elif line.strip().startswith("#") and insert_pos == i:
            insert_pos = i + 1
        else:
            break
    if not new_import.endswith("\n"):
        new_import += "\n"
    lines.insert(insert_pos, new_import)
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def remove_definition_from_file(file_path: Path, node: ast.AST, source_lines: List[str]):
    start_line = node.lineno - 1
    end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start_line + 1
    new_lines = source_lines[:start_line] + source_lines[end_line:]
    if start_line > 0 and new_lines[start_line - 1].strip() == "":
        pass
    elif start_line > 0:
        new_lines.insert(start_line, "\n")
    if start_line < len(new_lines) and new_lines[start_line].strip() == "":
        pass
    elif start_line < len(new_lines):
        new_lines.insert(start_line + 1, "\n")
    try:
        _ = ast.parse(new_lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines).rstrip() + "\n")
    except:
        print(f"{file_path} ast parse error")


def main():
    py_files = list(CURRENT_DIR.rglob("*.py"))
    py_files = [f for f in py_files if f.name != "utils.py" and f.name != "dedupe.py"]
    hash_to_defs: Dict[str, List[Tuple[Path, str, ast.AST, List[str]]]] = defaultdict(list)
    for fpath in py_files:
        defs = collect_definitions(fpath)
        for name, h, node in defs:
            with open(fpath, "r", encoding="utf-8") as f:
                source_lines = f.read().splitlines()
            hash_to_defs[h].append((fpath, name, node, source_lines))
    duplicates_found = False
    for h, items in hash_to_defs.items():
        if len(items) <= 1:
            continue
        duplicates_found = True
        canonical_file, canonical_name, canonical_node, _ = items[0]
        duplicates = items[1:]
        ensure_utils_file()
        utils_content = UTILS_FILE.read_text()
        print(f"Found duplicate: {canonical_name} ({len(items)} occurrences)")
        for dup_file, name, node, _ in duplicates:
            dup_src = node_to_source(node, dup_file.read_text().splitlines())
            print(f"  → Moving `{name}` from {dup_file} →.py")
            if not utils_content.endswith("\n\n"):
                utils_content += "\n\n"
            utils_content += dup_src.rstrip() + "\n\n"
            UTILS_FILE.write_text(utils_content)
    if not duplicates_found:
        print("No duplicate definitions found.")
    else:
        print("  - Duplicates moved to `utils.py`")


if __name__ == "__main__":
    main()
