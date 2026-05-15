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

import argparse
import ast
import os
import re
import sqlite3
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path("output")
DB_PATH = Path("/sdcard/ext.db")
ALLOWED_PYTHON_EXTENSIONS = (".py", "")


class EntityExtractor(ast.NodeVisitor):
    def __init__(self, source_content: str, original_path: Path) -> None:
        self.entities = []
        self.source_lines = source_content.splitlines(keepends=True)
        self.original_path = original_path
        self.scope_stack = []

    def _get_source_slice(self, node: ast.AST) -> str:
        start_line = node.lineno - 1
        end_line = node.end_lineno or node.lineno
        code_slice = self.source_lines[start_line:end_line]
        if node.col_offset is not None:
            code_slice[0] = code_slice[0][node.col_offset :]
        if node.end_col_offset is not None and node.end_col_offset > 0:
            last_line = code_slice[-1]
            code_slice[-1] = last_line[: node.end_col_offset]
        return "".join(code_slice)

    def _extract_and_save(self, node: ast.AST, entity_type: str, name: str):
        entity_code = self._get_source_slice(node)
        scope_prefix = "_".join(self.scope_stack)
        full_name = f"{scope_prefix}_{name}" if scope_prefix else name
        self.entities.append(
            {
                "name": name,
                "full_name": full_name,
                "type": entity_type,
                "code": entity_code,
                "path": str(self.original_path),
                "is_constant": entity_type == "constant",
                "is_class": entity_type == "class",
                "is_function": entity_type in {"function", "method"},
            }
        )

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if not self.scope_stack:
            self._extract_and_save(node, "function", node.name)

    def visit_ClassDef(self, node: ast.ClassDef):
        self._extract_and_save(node, "class", node.name)
        self.scope_stack.append(f"class_{node.name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Assign(self, node: ast.Assign):
        if not self.scope_stack and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            if re.match("^[A-Z_][A-Z0-9_]*$", target_name):
                self._extract_and_save(node, "constant", target_name)

    def generic_visit(self, node: ast.AST):
        super().generic_visit(node)


class EntityExtractor(ast.NodeVisitor):
    def __init__(self, source_content: str, original_path: Path) -> None:
        self.entities = []
        self.source_lines = source_content.splitlines(keepends=True)
        self.original_path = original_path
        self.scope_stack = []

    def _get_source_slice(self, node: ast.AST) -> str:
        start_line = node.lineno - 1
        end_line = node.end_lineno or node.lineno
        code_slice = self.source_lines[start_line:end_line]
        if node.col_offset is not None:
            code_slice[0] = code_slice[0][node.col_offset :]
        if node.end_col_offset is not None and node.end_col_offset > 0:
            last_line = code_slice[-1]
            code_slice[-1] = last_line[: node.end_col_offset]
        return "".join(code_slice)

    def _extract_and_save(self, node: ast.AST, entity_type: str, name: str):
        entity_code = self._get_source_slice(node)
        scope_prefix = "_".join(self.scope_stack)
        full_name = f"{scope_prefix}_{name}" if scope_prefix else name
        self.entities.append(
            {
                "name": name,
                "full_name": full_name,
                "type": entity_type,
                "code": entity_code,
                "path": str(self.original_path),
                "is_constant": entity_type == "constant",
                "is_class": entity_type == "class",
                "is_function": entity_type in {"function", "method"},
            }
        )

    def visit_FunctionDef(self, node: ast.FunctionDef):
        entity_type = "method" if self.scope_stack and self.scope_stack[-1].startswith("class_") else "function"
        self._extract_and_save(node, entity_type, node.name)
        self.scope_stack.append(f"func_{node.name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        entity_type = "method" if self.scope_stack and self.scope_stack[-1].startswith("class_") else "function"
        self._extract_and_save(node, entity_type, node.name)
        self.scope_stack.append(f"async_func_{node.name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef):
        self._extract_and_save(node, "class", node.name)
        self.scope_stack.append(f"class_{node.name}")
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_Assign(self, node: ast.Assign):
        if not self.scope_stack and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            if re.match("^[A-Z_][A-Z0-9_]*$", target_name):
                self._extract_and_save(node, "constant", target_name)

    def generic_visit(self, node: ast.AST):
        super().generic_visit(node)


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "\n        CREATE TABLE IF NOT EXISTS entities (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            name TEXT,\n            full_name TEXT,\n            type TEXT,\n            code TEXT,\n            path TEXT,\n            is_constant BOOLEAN,\n            is_class BOOLEAN,\n            is_function BOOLEAN\n        )\n    "
    )
    conn.commit()
    conn.close()


def save_entity_to_db(entity: dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "\n        INSERT INTO entities (name, full_name, type, code, path, is_constant, is_class, is_function)\n        VALUES (?, ?, ?, ?, ?, ?, ?, ?)\n    ",
        (
            entity["name"],
            entity["full_name"],
            entity["type"],
            entity["code"],
            entity["path"],
            entity["is_constant"],
            entity["is_class"],
            entity["is_function"],
        ),
    )
    conn.commit()
    conn.close()


def extract_entities_from_content(content: str, path: Path) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(content)
        extractor = EntityExtractor(content, path)
        extractor.visit(tree)
        return extractor.entities
    except SyntaxError:
        return []
    except Exception as e:
        print(f"Error parsing AST for {path}: {e}")
        return []


def is_python_file_no_extension(path: Path) -> bool:
    if path.suffix:
        return False
    try:
        with Path(path).open(encoding="utf-8", errors="ignore") as f:
            first_lines = "".join(f.readlines(1024))
            return bool(
                re.match("#!\\s*/.*python", first_lines)
                or ("def " in first_lines or "class " in first_lines or "import " in first_lines)
            )
    except:
        return False


def process_single_file(path: Path) -> list[dict[str, Any]]:
    try:
        if path.suffix == ".py" or is_python_file_no_extension(path):
            content = path.read_text(encoding="utf-8", errors="ignore")
            return extract_entities_from_content(content, path)
        return []
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Extract Python entities and save to database.")
    parser.add_argument("-db", "--database", action="store_true", help="Save extracted entities to the database")
    args = parser.parse_args()
    print(f"Starting analysis in {Path.cwd()}...")
    create_database()
    files_to_process = []
    current_dir = Path()
    for root, _, filenames in os.walk(current_dir):
        for name in filenames:
            path = Path(root) / name
            if path.is_relative_to(OUTPUT_DIR):
                continue
            if path.suffix in ALLOWED_PYTHON_EXTENSIONS or is_python_file_no_extension(path):
                files_to_process.append(path)
    if not files_to_process:
        print("No Python files found to process.")
        return
    all_entities = []
    for path in files_to_process:
        entities = process_single_file(path)
        all_entities.extend(entities)
    print(f"Processing complete. Extracted {len(all_entities)} entities.")
    if args.database:
        print(f"Saving entities to database at {DB_PATH}...")
        for entity in all_entities:
            save_entity_to_db(entity)
        print("All entities saved to database.")
    print("All tasks finished successfully!")


if __name__ == "__main__":
    main()
