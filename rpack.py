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

import argparse
import os
import re
import shutil
import sysconfig
from pathlib import Path

from wheel.wheelfile import WheelFile


def find_site_packages() -> Path:
    return Path(sysconfig.get_paths()["purelib"])


def list_installed_packages(site: Path):
    pkgs = {}
    for item in site.iterdir():
        if item.name.endswith(".dist-info"):
            name_version = item.name[:-10]
            m = re.match("(.+)-([\\w\\.]+)", name_version)
            if not m:
                continue
            pkg, version = (m.group(1), m.group(2))
            pkgs[pkg.lower()] = (pkg, version)
    return pkgs


def get_wheel_tags(dist_info: Path):
    wheel_file = dist_info / "WHEEL"
    if not wheel_file.exists():
        return ["py3-none-any"]
    content = wheel_file.read_text()
    tags = [line.split(":", 1)[1].strip() for line in content.splitlines() if line.startswith("Tag:")]
    return tags or ["py3-none-any"]


def copy_package_files(pkg: str, site: Path, dst: Path) -> None:
    candidates = [
        site / pkg,
        site / f"{pkg}.py",
        site / f"{pkg.replace('-', '_')}",
        site / f"{pkg.replace('-', '_')}.py",
    ]
    for c in candidates:
        if c.exists():
            if c.is_dir():
                shutil.copytree(c, dst / c.name)
            else:
                shutil.copy2(c, dst / c.name)
            break


def copy_dist_info(pkg: str, version: str, site: Path, dst: Path) -> Path:
    dist_dir = site / f"{pkg}-{version}.dist-info"
    out = dst / dist_dir.name
    shutil.copytree(dist_dir, out)
    return out


def copy_scripts(pkg: str, dst: Path) -> None:
    scripts_dir = Path(sysconfig.get_paths()["scripts"])
    if not scripts_dir.exists():
        return
    pattern = re.compile(f"^{pkg}(-.+)?$")
    for script in scripts_dir.iterdir():
        if script.is_file() and pattern.match(script.name):
            shutil.copy2(script, dst / script.name)


def build_wheel(pkg: str, version: str, tag: str, src_dir: Path, out_dir: Path):
    wheel_name = f"{pkg}-{version}-{tag}.whl"
    wheel_path = out_dir / wheel_name
    with WheelFile(str(wheel_path), "w") as wf:
        for root, _dirs, files in os.walk(src_dir):
            for file in files:
                full = Path(root) / file
                arcname = full.relative_to(src_dir)
                wf.write(str(full), str(arcname))
    return wheel_path


def repack(pkg: str, site: Path, out_repack: Path, out_whl: Path) -> None:
    pkg_lower = pkg.lower()
    installed = list_installed_packages(site)
    if pkg_lower not in installed:
        print(f"Package '{pkg}' not found.")
        return
    real_pkg, version = installed[pkg_lower]
    target_dir = out_repack / real_pkg
    target_dir.mkdir(parents=True, exist_ok=True)
    copy_package_files(real_pkg, site, target_dir)
    dist_info = copy_dist_info(real_pkg, version, site, target_dir)
    copy_scripts(real_pkg, target_dir)
    tags = get_wheel_tags(dist_info)
    tag = tags[0]
    wheel = build_wheel(real_pkg, version, tag, target_dir, out_whl)
    print(f"Repacked: {real_pkg} → {wheel}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Repack installed Python packages")
    parser.add_argument("packages", nargs="*", help="Package names")
    parser.add_argument("-a", "--all", action="store_true", help="Repack all installed pkgs")
    args = parser.parse_args()
    site = find_site_packages()
    out_repack = Path.home() / "tmp" / "repack"
    out_whl = Path.home() / "tmp" / "whl"
    out_repack.mkdir(parents=True, exist_ok=True)
    out_whl.mkdir(parents=True, exist_ok=True)
    if args.all:
        pkgs = list_installed_packages(site)
        for pkg, (real, _) in pkgs.items():
            repack(real, site, out_repack, out_whl)
    else:
        for pkg in args.packages:
            repack(pkg, site, out_repack, out_whl)


if __name__ == "__main__":
    main()
