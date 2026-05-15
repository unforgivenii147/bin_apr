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
import contextlib
import multiprocessing
import shutil
import subprocess
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


BASE_DIR = Path.home() / "tmp" / "debs"
BASE_DIR.mkdir(parents=True, exist_ok=True)


def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True)


def get_installed_packages():
    return run("dpkg-query -W -f='${Package}\n'").split()


def get_package_files(pkg):
    files = run(f"dpkg -L {pkg}").splitlines()
    return [f for f in files if Path(f).exists()]


def get_package_metadata(pkg):
    fmt = "${Package}\n${Version}\n${Architecture}\n${Maintainer}\n${Description}\n"
    out = run(f"dpkg-query -W -f='{fmt}' {pkg}").splitlines()
    return {"Package": out[0], "Version": out[1], "Architecture": out[2], "Maintainer": out[3], "Description": out[4]}


def create_control_file(path, meta) -> None:
    control_content = f"Package: {meta['Package']}\nVersion: {meta['Version']}\nArchitecture: {meta['Architecture']}\nMaintainer: {meta['Maintainer']}\nDescription: {meta['Description']}\n"
    (path / "control").write_text(control_content)


def copy_pkg_files(files, dest) -> None:
    for f in files:
        target = dest / f.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        with contextlib.suppress(Exception):
            shutil.copy2(f, target)


def build_tar_xz(source_dir, output_path) -> None:
    with tarfile.open(output_path, "w:xz") as tar:
        tar.add(source_dir, arcname=".")


def build_deb(pkg_dir, output_deb) -> None:
    debian_binary = pkg_dir / "debian-binary"
    debian_binary.write_text("2.0\n")
    control_tar = pkg_dir / "control.tar.xz"
    data_tar = pkg_dir / "data.tar.xz"
    build_tar_xz(pkg_dir / "DEBIAN", control_tar)
    build_tar_xz(pkg_dir / "files", data_tar)
    subprocess.run(f"ar r {output_deb} {debian_binary} {control_tar} {data_tar}", shell=True, check=True)


def process_package(pkg) -> str | None:
    try:
        pkg_dir = BASE_DIR / pkg
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)
        pkg_dir.mkdir()
        files_dir = pkg_dir / "files"
        debian_dir = pkg_dir / "DEBIAN"
        files_dir.mkdir()
        debian_dir.mkdir()
        meta = get_package_metadata(pkg)
        files = get_package_files(pkg)
        copy_pkg_files(files, files_dir)
        create_control_file(debian_dir, meta)
        output_deb = BASE_DIR / f"{pkg}.deb"
        build_deb(pkg_dir, output_deb)
        return f"[✔] {pkg} → {output_deb}"
    except Exception as e:
        return f"[✖] {pkg} FAILED: {e}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=multiprocessing.cpu_count(), help="Number of parallel workers")
    args = parser.parse_args()
    pkgs = ["tor"]
    print(f"[+] Building {len(pkgs)} packages using {args.workers} workers…\n")
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_package, pkg): pkg for pkg in pkgs}
        for future in as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    main()
