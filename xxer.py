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

import argparse
import gzip
import lzma
import os
import shutil
import tarfile
import zipfile
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from loguru import logger

import brotlicffi as brotli

import py7zr
import backports.zstd as zstd


SUPPORTED_EXTS = {
    ".tar",
    ".tar.xz",
    ".tar.gz",
    ".tar.br",
    ".tar.zst",
    ".tar.7z",
    ".tar.zip",
    ".xz",
    ".gz",
    ".br",
    ".zst",
    ".7z",
    ".zip",
}


@dataclass
class Result:
    ok: bool
    src: str
    dst: Optional[str] = None
    error: Optional[str] = None
    original_size: int = 0
    new_size: int = 0


def get_size(path: Path) -> int:
    """Returns the size of a file or directory in bytes."""
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = Path(dirpath) / f
                total_size += fp.stat().st_size
        return total_size
    return 0


def format_size(size_bytes: int) -> str:
    """Formats size in bytes to KB, MB, GB."""
    if size_bytes is None:
        return "N/A"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / (1024**2):.2f} MB"
    else:
        return f"{size_bytes / (1024**3):.2f} GB"


def has_compressed_suffix(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(ext) for ext in SUPPORTED_EXTS)


def output_name_for_file(path: Path, mode: str) -> Path:
    if mode == "xz":
        return path.with_name(path.name + ".xz")
    if mode == "gz":
        return path.with_name(path.name + ".gz")
    if mode == "brotli":
        return path.with_name(path.name + ".br")
    if mode == "zstd":
        return path.with_name(path.name + ".zst")
    if mode == "7z":
        return path.with_name(path.name + ".7z")
    if mode == "zip":
        return path.with_name(path.name + ".zip")
    raise ValueError(f"Unsupported mode: {mode}")


def output_name_for_dir(dir_path: Path, mode: str) -> Path:
    base = dir_path.name
    if mode == "xz":
        return dir_path.parent / f"{base}.tar.xz"
    if mode == "gz":
        return dir_path.parent / f"{base}.tar.gz"
    if mode == "brotli":
        return dir_path.parent / f"{base}.tar.br"
    if mode == "zstd":
        return dir_path.parent / f"{base}.tar.zst"
    if mode == "7z":
        return dir_path.parent / f"{base}.tar.7z"
    if mode == "zip":
        return dir_path.parent / f"{base}.tar.zip"
    raise ValueError(f"Unsupported mode: {mode}")


def atomic_write(src: Path, dst: Path, write_func, *args, **kwargs):
    """Writes to a temporary file and then atomically renames it to the destination."""
    temp_path = None
    try:
        # Create a temporary file in the same directory as the destination for atomic rename
        with tempfile.NamedTemporaryFile(delete=False, dir=dst.parent, prefix=f"{dst.stem}.") as tmp:
            temp_path = Path(tmp.name)
            write_func(src, temp_path, *args, **kwargs)  # write_func must handle its own opening/closing of files
        os.replace(temp_path, dst)  # Atomic rename
        return dst
    except Exception as e:
        logger.exception(f"Atomic write failed for {dst}")
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)  # Clean up temp file on error
        raise e


def tar_directory(src_dir: Path, tar_path: Path) -> None:
    with tarfile.open(tar_path, "w") as tf:
        tf.add(src_dir, arcname=src_dir.name)


def compress_file_xz(src: Path, dst: Path) -> None:
    with src.open("rb") as fin, lzma.open(dst, "wb", preset=9 | lzma.PRESET_EXTREME) as fout:
        shutil.copyfileobj(fin, fout)


def compress_file_gz(src: Path, dst: Path) -> None:
    with src.open("rb") as fin, gzip.open(dst, "wb", compresslevel=9) as fout:
        shutil.copyfileobj(fin, fout)


def compress_file_brotli(src: Path, dst: Path) -> None:
    if brotli is None:
        raise RuntimeError("brotlicffi is not installed")
    data = src.read_bytes()
    compressed = brotli.compress(data, quality=11)
    dst.write_bytes(compressed)


def compress_file_zstd(src: Path, dst: Path) -> None:
    if not src.stat().st_size:
        return
    data = src.read_bytes()
    compressed = zstd.compress(data)
    dst.write_bytes(compressed)


def compress_file_zip(src: Path, dst: Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(src, arcname=src.name)


def compress_file_7z(src: Path, dst: Path) -> None:
    if py7zr is None:
        raise RuntimeError("py7zr is not installed")
    with py7zr.SevenZipFile(dst, "w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": 9}]) as zf:
        zf.write(src, arcname=src.name)


def compress_tar_with_7z(tar_src: Path, dst: Path) -> None:
    if py7zr is None:
        raise RuntimeError("py7zr is not installed")
    with py7zr.SevenZipFile(dst, "w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": 9}]) as zf:
        zf.write(tar_src, arcname=tar_src.name)


def compress_tar_with_zip(tar_src: Path, dst: Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(tar_src, arcname=tar_src.name)


def compress_tar_with_gz(tar_src: Path, dst: Path) -> None:
    with tar_src.open("rb") as fin, gzip.open(dst, "wb", compresslevel=9) as fout:
        shutil.copyfileobj(fin, fout)


def compress_tar_with_xz(tar_src: Path, dst: Path) -> None:
    with tar_src.open("rb") as fin, lzma.open(dst, "wb", preset=9 | lzma.PRESET_EXTREME) as fout:
        shutil.copyfileobj(fin, fout)


def compress_tar_with_brotli(tar_src: Path, dst: Path) -> None:
    if brotli is None:
        raise RuntimeError("brotlicffi is not installed")
    data = tar_src.read_bytes()
    dst.write_bytes(brotli.compress(data, quality=11))


def compress_tar_with_zstd(tar_src: Path, dst: Path) -> None:
    if zstd is None:
        raise RuntimeError("zstandard is not installed")
    data = tar_src.read_bytes()
    dst.write_bytes(zstd.compress(data))


def compress_one(path_str: str, mode: str, is_dir: bool) -> Result:
    src = Path(path_str)
    dst = None
    tar_path = None
    original_size = get_size(src)
    result = Result(ok=False, src=str(src), original_size=original_size)

    try:
        if is_dir:
            tar_path = src.parent / f"{src.name}.tar"
            tar_directory(src, tar_path)

            dst = output_name_for_dir(src, mode)
            atomic_write(
                tar_path,
                dst,
                {
                    "xz": compress_tar_with_xz,
                    "gz": compress_tar_with_gz,
                    "brotli": compress_tar_with_brotli,
                    "zstd": compress_tar_with_zstd,
                    "7z": compress_tar_with_7z,
                    "zip": compress_tar_with_zip,
                }[mode],
            )

            # Safely remove original and temporary tar file
            tar_path.unlink(missing_ok=True)
            shutil.rmtree(str(src))
            #            src.rmdir()  # This will only succeed if rmdir is empty, which it should be after tarring
            result.dst = str(dst)
            result.new_size = get_size(dst)
            result.ok = True
            return result

        else:  # It's a file
            dst = output_name_for_file(src, mode)
            atomic_write(
                src,
                dst,
                {
                    "xz": compress_file_xz,
                    "gz": compress_file_gz,
                    "brotli": compress_file_brotli,
                    "zstd": compress_file_zstd,
                    "7z": compress_file_7z,
                    "zip": compress_file_zip,
                }[mode],
            )

            # Safely remove original file
            src.unlink()
            result.dst = str(dst)
            result.new_size = get_size(dst)
            result.ok = True
            return result

    except Exception as e:
        logger.exception(f"Failed to compress {src}")
        result.error = str(e)
        # Ensure originals are not removed if an error occurred
        if tar_path and tar_path.exists():
            tar_path.unlink(missing_ok=True)  # Clean up temp tar
        # Original src should remain untouched if compression failed
        return result


def decompress_one(path_str: str) -> Result:
    src = Path(path_str)
    extracted_path_str: Optional[str] = None
    temp_file_to_remove: Optional[Path] = None
    original_size = get_size(src)
    result = Result(ok=False, src=str(src), original_size=original_size)

    try:
        name = src.name.lower()
        dst_dir = src.parent

        # --- Tarred archives decompression ---
        if name.endswith(".tar.xz"):
            extracted_path = dst_dir / src.name[:-7]  # strip .tar.xz
            with tempfile.NamedTemporaryFile(delete=False, dir=dst_dir, suffix=".tar") as tmp_tar:
                temp_file_to_remove = Path(tmp_tar.name)
                with lzma.open(src, "rb") as fin:
                    shutil.copyfileobj(fin, tmp_tar)
            with tarfile.open(temp_file_to_remove, "r:") as tf:
                tf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".tar"):
            extracted_path = dst_dir / src.name[:-4]
            with tarfile.open(src, "r:") as tf:
                tf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".tar.gz"):
            extracted_path = dst_dir / src.name[:-6]  # strip .tar.gz
            with tempfile.NamedTemporaryFile(delete=False, dir=dst_dir, suffix=".tar") as tmp_tar:
                temp_file_to_remove = Path(tmp_tar.name)
                with gzip.open(src, "rb") as fin:
                    shutil.copyfileobj(fin, tmp_tar)
            with tarfile.open(temp_file_to_remove, "r:") as tf:
                tf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".tar.br"):
            if brotli is None:
                raise RuntimeError("brotlicffi is not installed")
            extracted_path = dst_dir / src.name[:-7]  # strip .tar.br
            data = brotli.decompress(src.read_bytes())
            with tempfile.NamedTemporaryFile(delete=False, dir=dst_dir, suffix=".tar") as tmp_tar:
                temp_file_to_remove = Path(tmp_tar.name)
                tmp_tar.write(data)
            with tarfile.open(temp_file_to_remove, "r:") as tf:
                tf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".tar.zst"):
            if zstd is None:
                raise RuntimeError("zstandard is not installed")
            extracted_path = dst_dir / src.name[:-8]  # strip .tar.zst
            with tempfile.NamedTemporaryFile(delete=False, dir=dst_dir, suffix=".tar") as tmp_tar:
                temp_file_to_remove = Path(tmp_tar.name)
                with src.open("rb") as fin:
                    decomp = zstd.decompress(fin.read())
                    tmp_tar.write(decomp)
            with tarfile.open(temp_file_to_remove, "r:") as tf:
                tf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".tar.7z"):
            if py7zr is None:
                raise RuntimeError("py7zr is not installed")
            extracted_path = dst_dir / src.name[:-7]  # strip .tar.7z
            with py7zr.SevenZipFile(src, "r") as zf:
                zf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".tar.zip"):
            extracted_path = dst_dir / src.name[:-8]  # strip .tar.zip
            with zipfile.ZipFile(src, "r") as zf:
                zf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)

        # --- Single file archives decompression ---
        elif name.endswith(".xz"):
            extracted_path = src.with_suffix("")
            with lzma.open(src, "rb") as fin, extracted_path.open("wb") as fout:
                shutil.copyfileobj(fin, fout)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".gz"):
            extracted_path = src.with_suffix("")
            with gzip.open(src, "rb") as fin, extracted_path.open("wb") as fout:
                shutil.copyfileobj(fin, fout)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".br"):
            if brotli is None:
                raise RuntimeError("brotlicffi is not installed")
            extracted_path = src.with_suffix("")
            out_bytes = brotli.decompress(src.read_bytes())
            extracted_path.write_bytes(out_bytes)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".zst"):
            extracted_name = src.stem  # Archive name without extension
            extracted_path = dst_dir / extracted_name
            if zstd is None:
                raise RuntimeError("zstandard is not installed")
            with src.open("rb") as fin, extracted_path.open("wb") as fout:
                decompressed_data = zstd.decompress(fin.read())
                if decompressed_data:
                    fout.write(decompressed_data)
                else:
                    print("error decompressing zstd file")
            extracted_path_str = str(extracted_path)

        elif name.endswith(".7z"):
            if py7zr is None:
                raise RuntimeError("py7zr is not installed")
            # py7zr extracts directly. We need to determine the extracted path.
            # This is heuristic and may need adjustment based on actual zip structure.
            extracted_name = src.stem  # Archive name without extension
            extracted_path = dst_dir / extracted_name
            with py7zr.SevenZipFile(src, "r") as zf:
                zf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)

        elif name.endswith(".zip"):
            extracted_path = src.with_suffix("")  # Heuristic for zip files
            with zipfile.ZipFile(src, "r") as zf:
                zf.extractall(path=dst_dir)
            extracted_path_str = str(extracted_path)  # Need to verify this path after extraction

        else:
            raise ValueError(f"Unsupported archive type: {src}")

        # Safely remove original archive and temp files
        src.unlink()
        if temp_file_to_remove and temp_file_to_remove.exists():
            temp_file_to_remove.unlink()
        if extracted_path_str:
            result.dst = extracted_path_str
            result.new_size = get_size(Path(extracted_path_str))
            result.ok = True
        else:  # Fallback if path could not be determined
            result.ok = True  # Assume success if no error, even if size can't be determined

        return result

    except Exception as e:
        logger.exception(f"Failed to decompress {src}")
        result.error = str(e)
        # Clean up any temporary files created during decompression
        if temp_file_to_remove and temp_file_to_remove.exists():
            temp_file_to_remove.unlink()
        # Original src should remain untouched if decompression failed
        return result


def collect_top_level_items(base: Path) -> list[Tuple[Path, bool]]:
    items = []
    for p in base.iterdir():
        if p.is_file():
            if not has_compressed_suffix(p):
                items.append((p, False))
        elif p.is_dir():
            # skip hidden dirs if desired? currently included
            if not has_compressed_suffix(p):
                items.append((p, True))
    return items


def main():
    parser = argparse.ArgumentParser(description="Compress/decompress current directory recursively.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--compress", action="store_true", help="Compress")
    group.add_argument("-d", "--decompress", action="store_true", help="Decompress")
    parser.add_argument(
        "-f", "--file", action="store_true", help="Treat input as file mode (default for files, no effect for dirs)"
    )
    parser.add_argument("-7", "--7z", dest="use_7z", action="store_true", help="Use py7zr")
    parser.add_argument("-z", "--zstd", action="store_true", help="Use zstandard")
    parser.add_argument("-x", "--xz", action="store_true", help="Use xz")
    parser.add_argument("-g", "--gz", action="store_true", help="Use gzip")
    parser.add_argument("-b", "--brotli", action="store_true", help="Use brotlicffi")
    parser.add_argument("--zip", action="store_true", help="Use zipfile")
    args = parser.parse_args()

    if not args.compress and not args.decompress:
        args.compress = True
        args.xz = True  # Default to xz compression if no mode specified

    overall_original_size = 0
    overall_new_size = 0
    processed_count = 0
    error_count = 0

    if args.decompress:
        targets = []
        for p in Path(".").iterdir():
            if p.is_file() and has_compressed_suffix(p):
                targets.append(str(p))

        if not targets:
            print("No compressed files found to decompress.")
            return

        print(f"Found {len(targets)} compressed files. Starting decompression...")
        with ProcessPoolExecutor() as ex:
            futures = [ex.submit(decompress_one, t) for t in targets]
            for fut in as_completed(futures):
                res = fut.result()
                processed_count += 1
                if res.ok:
                    print(
                        f"Decompressed: {res.src} -> {res.dst if res.dst else 'N/A'} | Size: {format_size(res.original_size)} -> {format_size(res.new_size)}"
                    )
                    overall_original_size += res.original_size
                    overall_new_size += res.new_size
                else:
                    error_count += 1
                    print(f"Failed to decompress: {res.src} - Error: {res.error}")

    # Compression logic
    else:  # Compress mode
        mode = "xz"  # Default mode
        if args.use_7z:
            mode = "7z"
        elif args.zstd:
            mode = "zstd"
        elif args.gz:
            mode = "gz"
        elif args.brotli:
            mode = "brotli"
        elif args.zip:
            mode = "zip"
        elif args.xz:
            mode = "xz"

        base = Path(".").resolve()
        items_to_process = collect_top_level_items(base)

        if not items_to_process:
            print("No files or directories to compress.")
            return

        print(f"Found {len(items_to_process)} items to compress using mode '{mode}'. Starting compression...")
        with ProcessPoolExecutor() as ex:
            futures = [ex.submit(compress_one, str(path), mode, is_dir) for path, is_dir in items_to_process]

            for fut in as_completed(futures):
                res = fut.result()
                processed_count += 1
                if res.ok:
                    print(
                        f"Compressed: {res.src} -> {res.dst} | Size: {format_size(res.original_size)} -> {format_size(res.new_size)}"
                    )
                    overall_original_size += res.original_size
                    overall_new_size += res.new_size
                else:
                    error_count += 1
                    print(f"Failed to compress: {res.src} - Error: {res.error}")

    # --- Final Summary ---
    print("\n--- Operation Summary ---")
    if processed_count == 0:
        print("No items were processed.")
        return

    if error_count > 0:
        print(f"Completed with {error_count} error(s).")

    if overall_original_size > 0:
        reduction = overall_original_size - overall_new_size
        percent_reduction = (reduction / overall_original_size) * 100 if overall_original_size > 0 else 0

        print(f"Total original size: {format_size(overall_original_size)}")
        print(f"Total new size:      {format_size(overall_new_size)}")
        print(f"Total size reduction: {format_size(abs(reduction))} ({percent_reduction:.2f}%)")
    else:
        print("Could not determine overall size changes.")


if __name__ == "__main__":
    main()
