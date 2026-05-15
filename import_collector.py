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

import ast
import importlib.metadata
import importlib.util
import sys
from pathlib import Path

from dh import is_python_file

PACKAGE_MAPPING = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "google": "google-cloud-storage",
    "dotenv": "python-dotenv",
    "bs4": "beautifulsoup4",
    "fitz": "pymupdf",
    "skimage": "scikit-image",
    "telegram": "python-telegram-bot",
    "dateutil": "python-dateutil",
    "git": "GitPython",
    "pydantic_core": "pydantic",
    "jwt": "PyJWT",
    "OpenGL": "PyOpenGL",
}


def get_imports_from_file(file_path):
    imports = set()
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update((n.name.split(".")[0] for n in node.names))
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports.add(node.module.split(".")[0])
    except (SyntaxError, UnicodeDecodeError):
        pass
    return imports


def check_status(module_name):
    try:
        importlib.metadata.distribution(module_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        spec = importlib.util.find_spec(module_name)
        return spec is not None


def main():
    cwd = Path()
    output_file = cwd / "importz.txt"
    pip_script = cwd / "install_deps.sh"
    all_imports = set()
    local_names = {p.stem for p in cwd.glob("*.py")}
    local_names.update({p.name for p in cwd.iterdir() if p.is_dir() and (p / "__init__.py").exists()})
    std_libs = getattr(sys, "stdlib_module_names", set())
    for path in cwd.rglob("*"):
        if is_python_file(path) and path.name not in {"importz.txt", "install_deps.sh"}:
            all_imports.update(get_imports_from_file(path))
    third_party = [
        imp for imp in all_imports if imp not in std_libs and imp not in local_names and (imp != "__future__")
    ]
    missing_for_pip = []
    already_installed = []
    for imp in sorted(third_party):
        if check_status(imp):
            already_installed.append(imp)
        else:
            pip_name = PACKAGE_MAPPING.get(imp, imp)
            missing_for_pip.append(pip_name)
    if third_party:
        output_file.write_text("\n".join(sorted(third_party)), encoding="utf-8")
        print(f"✅ Found {len(third_party)} 3rd-party dependencies.")
        if already_installed:
            print(f"📦 Already installed: {', '.join(already_installed)}")
        if missing_for_pip:
            install_cmd = f"pip install {' '.join(missing_for_pip)}"
            pip_script.write_text(f"#!/bin/sh\n{install_cmd}\n", encoding="utf-8")
            pip_script.chmod(pip_script.stat().st_mode | 73)
            print(f"⚠️  Missing: {', '.join(missing_for_pip)}")
            print(f"🚀 Run this to install missing: ./{pip_script.name}")
        else:
            if pip_script.exists():
                pip_script.unlink()
            print("✨ Environment is fully satisfied!")
    else:
        print("ℹ️ No 3rd-party imports found.")


if __name__ == "__main__":
    main()
