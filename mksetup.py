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

import shutil
import sys
import tempfile
import zipfile
from email.parser import Parser
from pathlib import Path


EXT_SUFFIXES = (".so", ".pyd", ".dll")


def read_entry_points(root: Path) -> dict[str, list[str]]:
    dist_info = next(root.glob("*.dist-info"), None)
    if not dist_info:
        return {}
    ep_file = dist_info / "entry_points.txt"
    if not ep_file.exists():
        return {}
    sections: dict[str, list[str]] = {}
    current_section = None
    for line in ep_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            sections[current_section] = []
            continue
        if current_section:
            sections[current_section].append(line)
    return sections


def extract_wheel(whl: Path, dst: Path) -> None:
    with zipfile.ZipFile(whl) as zf:
        zf.extractall(dst)


def load_root(input_path: Path) -> Path:
    if input_path.is_dir():
        return input_path.resolve()
    if input_path.suffix == ".whl":
        tmp = Path(tempfile.mkdtemp())
        extract_wheel(input_path, tmp)
        return tmp
    msg = "Input must be a .whl file or an unzipped wheel directory"
    raise SystemExit(msg)


def read_metadata(root: Path) -> dict:
    dist_info = next(root.glob("*.dist-info"), None)
    if not dist_info:
        msg = "No .dist-info directory found"
        raise RuntimeError(msg)
    meta_file = dist_info / "METADATA"
    meta = Parser().parsestr(meta_file.read_text())
    return {
        "name": meta["Name"],
        "version": meta["Version"],
        "summary": meta.get("Summary", ""),
        "install_requires": meta.get_all("Requires-Dist") or [],
    }


def find_extensions(root: Path) -> list[str]:
    return [".".join(f.relative_to(root).with_suffix("").parts) for f in root.rglob("*") if f.suffix in EXT_SUFFIXES]


def generate_setup_py(meta: dict, extensions: list[str], entry_points: dict[str, list[str]]) -> str:
    ext_block = (
        "from setuptools import Extension\n\next_modules = [\n"
        + "\n".join((f'''    Extension("{m}", sources=["{m.replace(".", "/")}.*"]),''' for m in extensions))
        + "\n]\n"
        if extensions
        else "ext_modules = []\n"
    )
    ep_block = ""
    if entry_points:
        formatted = "{\n"
        for section, values in entry_points.items():
            formatted += f'        "{section}": [\n'
            for v in values:
                formatted += f'            "{v}",\n'
            formatted += "        ],\n"
        formatted += "    }"
        ep_block = f"    entry_points={formatted},\n"
    return f'''from setuptools import setup, find_packages\n{ext_block}\nsetup(\n    name="{meta["name"]}",\n    version="{meta["version"]}",\n    description="{meta["summary"]}",\n    packages=find_packages() or ["."],\n    install_requires={meta["install_requires"]},\n    ext_modules=ext_modules,\n{ep_block})\n'''


def generate_pyproject_toml() -> str:
    return '[build-system]\nrequires = ["setuptools>=61", "wheel"]\nbuild-backend = "setuptools.build_meta"\n'


def main() -> None:
    if len(sys.argv) != 2:
        msg = "Usage: python mk_setuppy.py <wheel.whl | unzipped-dir>"
        raise SystemExit(msg)
    input_path = Path(sys.argv[1]).resolve()
    root = load_root(input_path)
    meta = read_metadata(root)
    entry_points = read_entry_points(root)
    extensions = find_extensions(root)
    out_dir = Path("output") / meta["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root, out_dir, dirs_exist_ok=True)
    (out_dir / "setup.py").write_text(generate_setup_py(meta, extensions, entry_points))
    (out_dir / "pyproject.toml").write_text(generate_pyproject_toml())
    print(f"✔ setup.py generated for {meta['name']}")
    print("✔ binary extensions detected" if extensions else "✔ pure Python package")


if __name__ == "__main__":
    main()
