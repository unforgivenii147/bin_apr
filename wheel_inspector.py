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

import zipfile
from pathlib import Path

from loguru import logger


class WheelInspector:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def log(self, message: str):
        if self.verbose:
            print(f"[INSPECT] {message}")

    def inspect_wheel(self, wheel_path: Path) -> dict:
        if not wheel_path.exists():
            return {"error": f"File not found: {wheel_path}"}
        try:
            with zipfile.ZipFile(wheel_path, "r") as zf:
                info = {
                    "filename": wheel_path.name,
                    "size_mb": wheel_path.stat().st_size / 1024.0,
                    "file_count": len(zf.namelist()),
                    "files": zf.namelist(),
                    "metadata": {},
                    "file_types": {},
                }
                metadata_files = [f for f in zf.namelist() if f.endswith("/METADATA")]
                if metadata_files:
                    metadata_content = zf.read(metadata_files[0]).decode("utf-8")
                    for line in metadata_content.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            info["metadata"][key.strip()] = value.strip()
                wheel_files = [f for f in zf.namelist() if f.endswith("/WHEEL")]
                if wheel_files:
                    wheel_content = zf.read(wheel_files[0]).decode("utf-8")
                    info["wheel_metadata"] = wheel_content
                info["file_types"] = {
                    ".py": len([f for f in zf.namelist() if f.endswith(".py")]),
                    ".so": len([f for f in zf.namelist() if f.endswith(".so")]),
                    ".pyd": len([f for f in zf.namelist() if f.endswith(".pyd")]),
                    ".c": len([f for f in zf.namelist() if f.endswith(".c")]),
                }
                return info
        except Exception as e:
            return {"error": str(e)}

    def validate_wheel(self, wheel_path: Path) -> tuple[bool, list[str]]:
        issues = []
        try:
            with zipfile.ZipFile(wheel_path, "r") as zf:
                files = zf.namelist()
                has_metadata = any((f.endswith("/METADATA") for f in files))
                if not has_metadata:
                    issues.append("Missing METADATA file")
                has_wheel = any((f.endswith("/WHEEL") for f in files))
                if not has_wheel:
                    issues.append("Missing WHEEL file")
                has_record = any((f.endswith("/RECORD") for f in files))
                if not has_record:
                    issues.append("Missing RECORD file")
                dist_info = [f for f in files if ".dist-info/" in f]
                if not dist_info:
                    issues.append("No dist-info directory found")
        except Exception as e:
            issues.append(f"Error reading wheel: {e!s}")
        return (len(issues) == 0, issues)

    def inspect_directory(self, directory: Path) -> list[dict]:
        wheels = list(directory.glob("*.whl"))
        results = []
        for wheel in wheels:
            info = self.inspect_wheel(wheel)
            print(info)
            is_valid, issues = self.validate_wheel(wheel)
            info["is_valid"] = is_valid
            info["issues"] = issues
            results.append(info)
        return results

    def print_inspection(self, wheel_path: Path):
        info = self.inspect_wheel(wheel_path)
        if "error" in info:
            print(f"Error: {info['error']}")
            return
        print(f"\n{'=' * 60}")
        print(f"Wheel: {info['filename']}")
        print(f"{'=' * 60}")
        print("\nBasic Info:")
        print(f"  Size: {info['size_mb']:.2f} KB")
        print(f"  Files: {info['file_count']}")
        if info["file_types"]:
            print("\nFile Types:")
            for ext, count in info["file_types"].items():
                if ext == ".py" and (not count or count == 1):
                    logger.debug(f"pkg:{wheel_path}\ncount : {count}")
                    outd = Path("/sdcard/test")
                    wn = wheel_path.name
                    outp = outd / wn
                    wheel_path.rename(outp)
                    continue
                if count > 0:
                    print(f"  {ext}: {count}")
        if info["metadata"]:
            print("\nMetadata:")
            for key, value in info["metadata"].items():
                if key in {"Name", "Version", "Summary", "Author"}:
                    print(f"  {key}: {value}")
        is_valid, issues = self.validate_wheel(wheel_path)
        print(f"\nValidation: {('✓ VALID' if is_valid else '✗ INVALID')}")
        if issues:
            print("Issues:")
            for issue in issues:
                print(f"  - {issue}")
        print(f"{'=' * 60}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Inspect and validate .whl files")
    parser.add_argument("wheel", nargs="?", help="Path to .whl file or directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    if not args.wheel:
        args.wheel = Path("/sdcard/whl")
    path = Path(args.wheel)
    inspector = WheelInspector(verbose=args.verbose)
    if path.is_file() and path.suffix == ".whl":
        inspector.print_inspection(path)
    elif path.is_dir():
        for p in path.rglob("*.whl"):
            inspector.print_inspection(p)


'\n        wheels = list(path.glob("*.whl"))\n        if not wheels:\n            print(f"No .whl files found in {path}")\n            return\n        print(f"\nInspecting {len(wheels)} .whl files...\n")\n        results = inspector.inspect_directory(path)\n        valid_count = sum(1 for r in results if r.get("is_valid", True))\n        invalid_count = len(results) - valid_count\n        for result in results:\n            status = "✓" if result.get("is_valid", True) else "✗"\n            size = result.get("size_mb", 0)\n            files = result.get("file_count", 0)\n            print(f"{status} {result[\'filename\']:<50} {size:>.2f} KB ({files} files)")\n        print(f"\nValid: {valid_count}/{len(results)}")\n        print(f"Invalid: {invalid_count}/{len(results)}")\n    else:\n        print(f"Invalid path: {path}")\n        sys.exit(1)\n'
if __name__ == "__main__":
    main()
