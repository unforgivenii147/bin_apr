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


def create_initpy(current_dir, pkg_name):
    src_dir = current_dir / "src"
    pkg_dir = src_dir / pkg_name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    init_file = pkg_dir / "__init__.py"
    init_content = "__version__ = (1, 4, 7)\nfrom contextlib import suppress\nfrom importlib.metadata import PackageNotFoundError,version\nwith suppress(PackageNotFoundError):\n    __version__ = version(__name__)\n"
    if not init_file.exists():
        init_file.write_text(init_content, encoding="utf-8")


def create_readme(current_dir, pkg_name):
    readme_file = current_dir / "README.md"
    readme_content = f"# {pkg_name}\nA Python package named {pkg_name}.\n```bash\npip install -e .\n```\nUsage\n```python\nimport {pkg_name}\n```\n"
    if not readme_file.exists():
        readme_file.write_text(readme_content, encoding="utf-8")


def create_pyproject(current_dir, pkg_name):
    pyproject_file = current_dir / "pyproject.toml"
    pyproject_content = f'[build-system]\nrequires = ["setuptools>=61.0", "wheel"]\nbuild-backend = "setuptools.build_meta"\n[project]\nname = "{pkg_name}"\nversion = "1.4.7"\ndescription = "A Python package named {pkg_name}"\nreadme = "README.md"\nauthors = [\n{{name = "Isaac Onagh", email = "mkalafsaz@gmail.com"}},\n]\nclassifiers = [\n"Programming Language :: Python :: 3",\n"Operating System :: OS Independent",\n]\nrequires-python = ">=3.9"\n[tool.setuptools.packages.find]\nwhere = ["src"]\n'
    if not pyproject_file.exists():
        pyproject_file.write_text(pyproject_content, encoding="utf-8")


def create_setuppy(current_dir, pkg_name):
    setuppy_file = current_dir / "setup.py"
    setuppy_content = f'from pathlib import Path\nfrom setuptools import setup, find_packages\nimport re\nhere = Path(__file__).parent\nversion_re = re.compile(r"__version__ = (\\(.*?\\))")\nversion = "1.4.7"\nfor line in Path("src/{pkg_name}/__init__.py").read_text().splitlines():\n    match = version_re.search(line)\n    if match:\n        version = eval(match.group(1))\n        break\nsetup(\n    name="{pkg_name}",\n    version=".".join(map(str, version)),\n    description=f"python pkg named {pkg_name}",\n    packages=find_packages(),\n)\n'
    if not setuppy_file.exists():
        setuppy_file.write_text(setuppy_content, encoding="utf-8")


def create_python_project(pkg_name):
    cwd = Path.cwd()
    create_initpy(cwd, pkg_name)
    create_readme(cwd, pkg_name)
    create_pyproject(cwd, pkg_name)
    create_setuppy(cwd, pkg_name)


def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    pkg = sys.argv[1]
    create_python_project(pkg)


if __name__ == "__main__":
    main()
