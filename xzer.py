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

import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

import lzma_mt

_executor = asyncio.Semaphore(4)


def fsz(size: float) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(size) < 1024.0:
            return f"{size:3.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PiB"


async def compress_folder_async(folder_path: Path, output_base_name: str, format="tar") -> bool:
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, lambda: shutil.make_archive(output_base_name, format, str(folder_path)))
        return True
    except Exception as e:
        print(f"Failed to compress folder {folder_path} → {output_base_name}: {e}")
        return False


async def atomic_write_async(data: bytes, final_path: Path) -> bool:
    temp_dir = final_path.parent
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = None
    loop = asyncio.get_running_loop()
    try:

        def _create_temp():
            with tempfile.NamedTemporaryFile(mode="wb", dir=temp_dir, prefix=".tmp_", suffix=".xz", delete=False) as f:
                f.write(data)
                f.flush()
            return Path(f.name)

        temp_path = await loop.run_in_executor(None, _create_temp)
        await loop.run_in_executor(None, lambda: temp_path.rename(final_path))
        print(f"Atomically written to: {final_path}")
        return True
    except Exception as e:
        print(f"Atomic write failed for {final_path}: {e}")
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
    return False


def safe_delete(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        if path.is_dir():
            shutil.rmtree(str(path))
        else:
            path.unlink()
        return True
    except PermissionError:
        return False
    except Exception as e:
        return False


async def compress_file_async(path: Path) -> bool:
    compressed_path = path.with_suffix(path.suffix + ".xz")
    if compressed_path.exists():
        return False
    try:
        loop = asyncio.get_running_loop()

        def _read():
            with path.open("rb") as f:
                return f.read()

        data = await loop.run_in_executor(None, _read)
        original_size = path.stat().st_size

        def _compress():
            return lzma_mt.compress(data, threads=4, preset=lzma_mt.PRESET_EXTREME)

        compressed_data = await loop.run_in_executor(None, _compress)
        if not await atomic_write_async(compressed_data, compressed_path):
            return False
        compressed_size = compressed_path.stat().st_size
        if not compressed_size:
            print(f"Compressed file empty: {compressed_path}")
            return False
        if not safe_delete(path):
            print(f"Failed to delete {path}")
            return False
        reduction = ((original_size - compressed_size) / original_size) * 100
        print(f"{path.name}|{fsz(original_size)} → {fsz(compressed_size)} ratio: {reduction:.2f}%")
        return True
    except Exception as e:
        print(f"Compression failed for {path}: {e}")
        return False


def get_files(directory: Path) -> list[Path]:
    return [p for p in directory.glob("*") if p.is_file() and (not p.is_symlink()) and should_compress(p)]


def get_dirs(directory: Path) -> list[Path]:
    return [p for p in directory.glob("*") if not p.is_symlink() and p.is_dir()]


def should_compress(path):
    path = Path(path)
    try:
        if path.is_symlink():
            return False
        if not path.is_file():
            return False
        compressed_extensions = (".xz", ".br", ".7z")
        if path.suffix in compressed_extensions:
            return False
        return path.stat().st_size
    except (OSError, PermissionError):
        return False


async def main_async() -> None:
    sys.argv[1:]
    cwd = Path.cwd()
    dirs_to_compress = get_dirs(cwd)
    if dirs_to_compress:
        for dir_path in sorted(dirs_to_compress):
            print(f"compressing {dir_path.relative_to(cwd)}")
            if await compress_folder_async(dir_path, str(dir_path.parent / dir_path.name), format="tar"):
                print(f"compressed {dir_path.relative_to(cwd)}")
                safe_delete(dir_path)
    files_to_compress = get_files(cwd)
    if not files_to_compress:
        print("No files to compress")
        return
    total_original = 0
    total_compressed = 0
    successful = 0
    for i, path in enumerate(sorted(files_to_compress), 1):
        print(f"\n[{i}/{len(files_to_compress)}] {path.name}")
        orig_size = path.stat().st_size
        total_original += orig_size
        if await compress_file_async(path):
            successful += 1
        compressed_path = path.with_suffix(path.suffix + ".xz")
        if compressed_path.exists():
            total_compressed += compressed_path.stat().st_size
    if successful > 0:
        savings = total_original - total_compressed
        savings_percent = savings / total_original * 100
        print(f"Space saved: {fsz(savings)} {savings_percent:.1f}%")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
