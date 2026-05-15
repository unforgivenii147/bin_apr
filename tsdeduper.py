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
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from tree_sitter import Parser
from tree_sitter_languages import get_language

OUTPUT_FILE = "utils.py"


@dataclass(frozen=True)
class Item:
    kind: str
    name: str
    source: str
    path: str
    hash: str


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_parser() -> Parser:
    parser = Parser()
    parser.language = get_language("python")
    return parser


def node_text(src: bytes, node) -> str:
    return src[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def is_const_name(name: str) -> bool:
    return name.isupper()


def extract_items(path: Path, parser: Parser) -> List[Item]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    src = text.encode("utf-8", errors="replace")
    tree = parser.parse(src)
    root = tree.root_node

    items: List[Item] = []

    for node in root.children:
        # function
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name = node_text(src, name_node)
            code = node_text(src, node)
            items.append(
                Item(
                    kind="function",
                    name=name,
                    source=code,
                    path=str(path),
                    hash=sha256_text(code),
                )
            )

        # class
        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if not name_node:
                continue
            name = node_text(src, name_node)
            code = node_text(src, node)
            items.append(
                Item(
                    kind="class",
                    name=name,
                    source=code,
                    path=str(path),
                    hash=sha256_text(code),
                )
            )

        # constants (top-level assignment)
        elif node.type in {"expression_statement", "assignment"}:
            code = node_text(src, node)

            # tree-sitter-python usually represents "X = 1" as assignment
            # under an expression_statement or directly as assignment depending on grammar version
            assign_node = node
            if node.type == "expression_statement" and node.children:
                assign_node = node.children[0]

            if assign_node.type != "assignment":
                continue

            # simplest case: single identifier on LHS
            if len(assign_node.children) < 3:
                continue

            lhs = assign_node.children[0]
            if lhs.type != "identifier":
                continue

            name = node_text(src, lhs)
            if not is_const_name(name):
                continue

            items.append(
                Item(
                    kind="const",
                    name=name,
                    source=code,
                    path=str(path),
                    hash=sha256_text(code),
                )
            )

    return items


def write_utils_file(dups: Dict[str, Item], output: Path) -> None:
    lines = [
        "# Auto-generated file",
        "# Contains duplicate top-level constants, functions, and classes.",
        "",
    ]

    seen = set()
    for h, item in dups.items():
        if h in seen:
            continue
        seen.add(h)
        lines.append(f"# Duplicate {item.kind}: {item.name}")
        lines.append(f"# Source: {item.path}")
        lines.append(item.source)
        lines.append("")

    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = make_parser()
    base = Path(".").resolve()

    seen: Dict[str, Item] = {}
    dups: Dict[str, Item] = {}

    for root, _, files in os.walk(base):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            if fname == OUTPUT_FILE:
                continue

            path = Path(root) / fname
            for item in extract_items(path, parser):
                if item.hash in seen:
                    dups[item.hash] = seen[item.hash]
                else:
                    seen[item.hash] = item

    out = base / OUTPUT_FILE
    if dups:
        write_utils_file(dups, out)
        print(f"Found {len(dups)} duplicate items.")
        print(f"Wrote them to: {out}")
    else:
        print("No duplicates found.")


if __name__ == "__main__":
    main()
