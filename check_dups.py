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
import copy
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

from dh import get_pyfiles, gsz, mpf3

N_JOBS = -1


@dataclass
class Decl:
    kind: str
    name: str
    lineno: int
    end_lineno: int
    source: str
    content_hash: str


class Normalizer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node = copy.deepcopy(node)
        node.name = "__NAME__"
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        node = copy.deepcopy(node)
        node.name = "__NAME__"
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        node = copy.deepcopy(node)
        node.name = "__NAME__"
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        node = copy.deepcopy(node)
        if isinstance(node.ctx, ast.Store):
            node.id = "__VAR__"
        return node


def stable_hash(node: ast.AST) -> str:
    node = copy.deepcopy(node)
    node = Normalizer().visit(node)
    ast.fix_missing_locations(node)
    dumped = ast.dump(node, annotate_fields=True, include_attributes=False)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()


def get_source_segment(lines, lineno, end_lineno):
    return "".join(lines[lineno - 1 : end_lineno])


def is_simple_top_level_assign(node):
    if not isinstance(node, ast.Assign):
        return False
    for target in node.targets:
        if isinstance(target, ast.Name):
            continue
        if isinstance(target, (ast.Tuple, ast.List)):
            return False
        return False
    return True


def extract_assign_names(node):
    names = []
    for target in node.targets:
        if isinstance(target, ast.Name):
            names.append(target.id)
    return names


def build_decl_for_assign(node, lines):
    names = extract_assign_names(node)
    source = get_source_segment(lines, node.lineno, node.end_lineno)
    h = stable_hash(node)
    decls = []
    for name in names:
        decls.append(
            Decl(
                kind="assign", name=name, lineno=node.lineno, end_lineno=node.end_lineno, source=source, content_hash=h
            )
        )
    return decls


def build_decl(node, kind, name, lines):
    return Decl(
        kind=kind,
        name=name,
        lineno=node.lineno,
        end_lineno=node.end_lineno,
        source=get_source_segment(lines, node.lineno, node.end_lineno),
        content_hash=stable_hash(node),
    )


def process_file(src_path):
    dup_path = src_path.parent / f"{src_path.stem}_dups.py"
    text = src_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        print(f"Syntax error in {src_path}: {e}")
        sys.exit(1)
    decls = []
    top_level_nodes = []
    for node in tree.body:
        if is_simple_top_level_assign(node):
            decls.extend(build_decl_for_assign(node, lines))
            top_level_nodes.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decls.append(build_decl(node, "function", node.name, lines))
            top_level_nodes.append(node)
        elif isinstance(node, ast.ClassDef):
            decls.append(build_decl(node, "class", node.name, lines))
            top_level_nodes.append(node)
    seen_name = set()
    seen_hash = set()
    duplicate_ranges = []
    duplicate_reasons = []
    already_marked_ranges = set()
    for decl in decls:
        key_name = (decl.kind, decl.name)
        key_hash = (decl.kind, decl.content_hash)
        rng = (decl.lineno, decl.end_lineno)
        is_dup = False
        reason = None
        if key_name in seen_name:
            is_dup = True
            reason = f"duplicate {decl.kind} name: {decl.name}"
        elif key_hash in seen_hash:
            is_dup = True
            reason = f"duplicate {decl.kind} content hash: {decl.name}"
        else:
            seen_name.add(key_name)
            seen_hash.add(key_hash)
        if is_dup and rng not in already_marked_ranges:
            duplicate_ranges.append(rng)
            duplicate_reasons.append((decl, reason))
            already_marked_ranges.add(rng)
    if not duplicate_ranges:
        print("No duplicate top-level assignments/functions/classes found.")
        return
    remove_lines = set()
    for start, end in duplicate_ranges:
        remove_lines.update(range(start, end + 1))
    kept_lines = [line for i, line in enumerate(lines, start=1) if i not in remove_lines]
    out = []
    out.append(f"\n# Duplicates moved from {src_path.name}\n")
    for decl, reason in duplicate_reasons:
        out.append(f"\n# {reason} @ lines {decl.lineno}-{decl.end_lineno}\n")
        out.append(decl.source)
        if not decl.source.endswith("\n"):
            out.append("\n")
    src_path.write_text("".join(kept_lines), encoding="utf-8")
    with dup_path.open("a", encoding="utf-8") as f:
        f.write("".join(out))
    print(f"Updated {src_path} in place")
    print(f"Moved {len(duplicate_ranges)} duplicate declaration block(s) to {dup_path}")


def main():
    root_dir = Path.cwd()
    before = gsz(root_dir)
    args = sys.argv[1:]
    files = []
    if args:
        for arg in args:
            p = Path(arg)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                files.extend(get_pyfiles(p, recursive=True))
    else:
        files = get_pyfiles(root_dir)
    results = mpf3(process_file, files)
    for result in results:
        if result:
            pass


if __name__ == "__main__":
    sys.exit(main())
