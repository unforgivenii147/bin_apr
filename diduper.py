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
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from tree_sitter import Parser

# tree-sitter-languages provides a prebuilt Python grammar
from tree_sitter_languages import get_language


OUTPUT_FILE = "utils.py"
SKIP_FILES = {OUTPUT_FILE, Path(__file__).name}


@dataclass(frozen=True)
class Item:
    kind: str  # constant / function / class
    name: str
    source: str
    file_path: str
    hash: str


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_python_parser() -> Parser:
    parser = Parser()
    lang = get_language("python")
    # tree-sitter 0.25.x uses parser.language assignment
    parser.language = lang
    return parser


def node_text(source_bytes: bytes, node) -> str:
    return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def is_const_name(name: str) -> bool:
    return name.isupper()


def extract_items_from_file(path: Path, parser: Parser) -> List[Item]:
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    src_bytes = source.encode("utf-8", errors="replace")
    tree = parser.parse(src_bytes)
    root = tree.root_node

    items: List[Item] = []

    # Only inspect top-level declarations
    for child in root.children:
        if child.type == "function_definition":
            name_node = child.child_by_field_name("name")
            if name_node is None:
                continue
            name = node_text(src_bytes, name_node)
            code = node_text(src_bytes, child)
            items.append(
                Item(
                    kind="function",
                    name=name,
                    source=code,
                    file_path=str(path),
                    hash=sha256_text(code),
                )
            )

        elif child.type == "class_definition":
            name_node = child.child_by_field_name("name")
            if name_node is None:
                continue
            name = node_text(src_bytes, name_node)
            code = node_text(src_bytes, child)
            items.append(
                Item(
                    kind="class",
                    name=name,
                    source=code,
                    file_path=str(path),
                    hash=sha256_text(code),
                )
            )

        elif child.type == "expression_statement":
            # Possible top-level assignment forms:
            #   X = 1
            #   X: int = 1
            # We only treat ALL_CAPS names as constants.
            expr = child.children[0] if child.children else None
            if expr is None:
                continue

            if expr.type == "assignment":
                # left side may be a name or tuple; we only accept single name
                if len(expr.children) < 3:
                    continue
                lhs = expr.children[0]
                rhs = expr.children[-1]
                if lhs.type != "identifier":
                    continue
                name = node_text(src_bytes, lhs)
                if not is_const_name(name):
                    continue
                code = node_text(src_bytes, child)
                items.append(
                    Item(
                        kind="const",
                        name=name,
                        source=code,
                        file_path=str(path),
                        hash=sha256_text(code),
                    )
                )

            elif expr.type == "assignment_expression":
                # Some grammars may parse differently; keep a fallback
                pass

        elif child.type == "assignment":
            # Some tree-sitter Python grammar versions may expose top-level assignment directly
            if len(child.children) < 3:
                continue
            lhs = child.children[0]
            if lhs.type != "identifier":
                continue
            name = node_text(src_bytes, lhs)
            if not is_const_name(name):
                continue
            code = node_text(src_bytes, child)
            items.append(
                Item(
                    kind="const",
                    name=name,
                    source=code,
                    file_path=str(path),
                    hash=sha256_text(code),
                )
            )

    return items


def write_utils_file(duplicates: Dict[str, Item], output_path: Path) -> None:
    # Write one representative copy per duplicate hash
    blocks = []
    seen_hashes = set()

    for h, item in duplicates.items():
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        blocks.append(f"# Duplicate {item.kind}: {item.name}\n# Source: {item.file_path}\n{item.source}\n")

    content = (
        "# Auto-generated by find_duplicates_ts.py\n"
        "# Contains duplicate constants / functions / classes found in the project.\n\n" + "\n".join(blocks)
    )

    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = get_python_parser()
    all_items: Dict[str, Item] = {}
    duplicates: Dict[str, Item] = {}

    base_dir = Path(".").resolve()

    for root, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            if fname in SKIP_FILES:
                continue

            path = Path(root) / fname
            items = extract_items_from_file(path, parser)

            for item in items:
                if item.hash in all_items:
                    # exact duplicate detected
                    duplicates[item.hash] = all_items[item.hash]
                else:
                    all_items[item.hash] = item

    output_path = base_dir / OUTPUT_FILE
    if duplicates:
        write_utils_file(duplicates, output_path)
        print(f"Found {len(duplicates)} duplicate items.")
        print(f"Wrote representative copies to: {output_path}")
    else:
        print("No duplicates found.")


if __name__ == "__main__":
    main()
