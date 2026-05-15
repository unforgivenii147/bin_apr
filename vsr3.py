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
import csv
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


try:
    from tqdm import tqdm
except ImportError:
    print("Error: tqdm is required. Install it with: pip install tqdm")
    sys.exit(1)


def find_dist_info_dirs(site_packages: Path) -> list[Path]:
    dist_dirs = []
    dist_dirs.extend(site_packages.glob("*.dist-info"))
    dist_dirs.extend(site_packages.glob("*.egg-info"))
    return sorted(dist_dirs)


def get_package_name_version(dist_dir: Path) -> tuple:
    name = dist_dir.name
    if name.endswith(".dist-info"):
        name = name[:-10]
    elif name.endswith(".egg-info"):
        name = name[:-9]
    parts = name.rsplit("-", 1)
    if len(parts) == 2:
        return (parts[0], parts[1])
    return (parts[0], "0.0.0")


def read_record_file(dist_dir: Path, site_packages: Path) -> tuple[list[Path], set[Path]]:
    record_file = dist_dir / "RECORD"
    if not record_file.exists():
        return ([], set())
    existing_files = []
    missing_files = set()
    with Path(record_file).open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0]:
                continue
            file_path = row[0]
            full_path = Path(file_path) if Path(file_path).is_absolute() else site_packages / file_path
            if full_path.suffix == ".pyc":
                continue
            if full_path.exists():
                existing_files.append(full_path)
            else:
                missing_files.add(full_path)
    return (existing_files, missing_files)


def get_wheel_tag(dist_dir: Path) -> str | None:
    wheel_file = dist_dir / "WHEEL"
    if not wheel_file.exists():
        return None
    with Path(wheel_file).open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("Tag:"):
                return line.split(":", 1)[1].strip()
    return None


def copy_files_to_temp(files: list[Path], site_packages: Path, temp_dir: Path):
    for file_path in files:
        try:
            rel_path = file_path.relative_to(site_packages)
        except ValueError:
            rel_path = Path(file_path.name)
        dest_path = temp_dir / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.is_file():
            shutil.copy2(file_path, dest_path)
        elif file_path.is_dir():
            shutil.copytree(file_path, dest_path, dirs_exist_ok=True)


def create_wheel(pkg_name: str, pkg_version: str, temp_dir: Path, output_dir: Path, wheel_tag: str | None) -> bool:
    try:
        wheel_name = f"{pkg_name}-{pkg_version}"
        if wheel_tag:
            wheel_name += f"-{wheel_tag}"
        else:
            wheel_name += "-py3-none-any"
        wheel_file = output_dir / f"{wheel_name}.whl"
        cmd = [sys.executable, "-m", "wheel", "pack", str(temp_dir), "-d", str(output_dir)]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        import zipfile

        with zipfile.ZipFile(wheel_file, "w", zipfile.ZIP_DEFLATED) as whl:
            for root, _dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    whl.write(file_path, arcname)
        return True
    except Exception as e:
        print(f"Error creating wheel: {e}")
        return False


def repack_package(dist_dir: Path, site_packages: Path, output_dir: Path, not_repacked_dir: Path) -> bool:
    pkg_name, pkg_version = get_package_name_version(dist_dir)
    existing_files, missing_files = read_record_file(dist_dir, site_packages)
    if not existing_files:
        return False
    has_missing_critical = any((f.suffix in {".py", ""} or f.is_dir() for f in missing_files))
    if has_missing_critical:
        pkg_not_repacked = not_repacked_dir / pkg_name
        pkg_not_repacked.mkdir(parents=True, exist_ok=True)
        for file_path in existing_files:
            try:
                rel_path = file_path.relative_to(site_packages)
                dest = pkg_not_repacked / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if file_path.is_file():
                    shutil.copy2(file_path, dest)
            except Exception as e:
                msg = f"error {e}"
                raise Exception(msg) from e
        return False
    wheel_tag = get_wheel_tag(dist_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        copy_files_to_temp(existing_files, site_packages, temp_path)
        return create_wheel(pkg_name, pkg_version, temp_path, output_dir, wheel_tag)


def main():
    parser = argparse.ArgumentParser(description="Repack installed Python packages as wheels")
    parser.add_argument("packages", nargs="*", help="Package names to repack")
    parser.add_argument("-a", "--all", action="store_true", help="Repack all installed packages")
    args = parser.parse_args()
    if not args.all and (not args.packages):
        parser.error("Specify package names or use -a/--all")
    "\n    site_packages = (\n        Path(sys.prefix)\n        / 'lib'\n        / f'python{sys.version_info.major}.{sys.version_info.minor}'\n        / 'site-packages'\n    )\n    if not site_packages.exists():\n        site_packages = Path(sys.prefix) / 'Lib' / 'site-packages'\n    "
    site_packages = Path.cwd()
    output_dir = Path.home() / "tmp" / "whl"
    not_repacked_dir = Path.home() / "tmp" / "not_repacked"
    output_dir.mkdir(parents=True, exist_ok=True)
    not_repacked_dir.mkdir(parents=True, exist_ok=True)
    all_dist_dirs = find_dist_info_dirs(site_packages)
    if not args.all:
        pkg_set = set(args.packages)
        all_dist_dirs = [d for d in all_dist_dirs if get_package_name_version(d)[0] in pkg_set]
    success_count = 0
    failed_count = 0
    with tqdm(total=len(all_dist_dirs), desc="Repacking packages") as pbar:
        for dist_dir in all_dist_dirs:
            pkg_name, _ = get_package_name_version(dist_dir)
            pbar.set_description(f"Repacking {pkg_name}")
            if repack_package(dist_dir, site_packages, output_dir, not_repacked_dir):
                success_count += 1
            else:
                failed_count += 1
            pbar.update(1)
    print(f"\n✓ Successfully repacked: {success_count}")
    print(f"✗ Failed to repack: {failed_count}")
    print(f"\nWheels saved to: {output_dir}")
    if failed_count > 0:
        print(f"Failed packages copied to: {not_repacked_dir}")


if __name__ == "__main__":
    main()
