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

import ast
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


class ImportVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self._nesting_level = 0
        self.non_top_level_imports: list[ast.stmt] = []

    def _is_top_level(self) -> bool:
        return self._nesting_level == 0

    def _visit_nested(self, node: ast.AST):
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_nested(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_nested(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self._visit_nested(node)

    def visit_For(self, node: ast.For):
        self._visit_nested(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self._visit_nested(node)

    def visit_While(self, node: ast.While):
        self._visit_nested(node)

    def visit_If(self, node: ast.If):
        self._visit_nested(node)

    def visit_With(self, node: ast.With):
        self._visit_nested(node)

    def visit_AsyncWith(self, node: ast.AsyncWith):
        self._visit_nested(node)

    def visit_Try(self, node: ast.Try):
        self._visit_nested(node)

    def visit_Import(self, node: ast.Import):
        if not self._is_top_level():
            self.non_top_level_imports.append(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if not self._is_top_level():
            self.non_top_level_imports.append(node)
        self.generic_visit(node)


def find_python_files(root: Path) -> Iterable[Path]:
    return root.rglob("*.py")


def format_import(node: ast.stmt) -> str:
    if isinstance(node, ast.Import):
        parts = []
        for alias in node.names:
            if alias.asname:
                parts.append(f"{alias.name} as {alias.asname}")
            else:
                parts.append(alias.name)
        return "import " + ", ".join(parts)
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        parts = []
        for alias in node.names:
            if alias.asname:
                parts.append(f"{alias.name} as {alias.asname}")
            else:
                parts.append(alias.name)
        level_dots = "." * (node.level or 0)
        module_str = level_dots + module if module else level_dots
        return f"from {module_str} import " + ", ".join(parts)
    return "<unknown import>"


def inspect_file(path: Path):
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        source = path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        print(f"[WARN] Skipping {path} (syntax error: {e})")
        return []
    visitor = ImportVisitor()
    visitor.visit(tree)
    results = []
    for node in visitor.non_top_level_imports:
        lineno = getattr(node, "lineno", "?")
        results.append((lineno, format_import(node)))
    return results


def main():
    root = Path.cwd()
    any_found = False
    for py_file in find_python_files(root):
        imports = inspect_file(py_file)
        if not imports:
            continue
        any_found = True
        print(f"\n{py_file}:")
        for lineno, stmt in imports:
            print(f"  line {lineno}: {stmt}")
    if not any_found:
        print("No non-top-level imports found.")


if __name__ == "__main__":
    main()
