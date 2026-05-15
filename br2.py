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
import pathlib
import sys
import tarfile
from contextlib import contextmanager
from typing import List

try:
    import brotli
except ImportError:
    print("❌ Error: brotlicffi not installed. Run: pip install brotlicffi", file=sys.stderr)
    sys.exit(1)
CHUNK_SIZE = 1024 * 1024
LARGE_FILE_THRESHOLD = 5 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Brotli compression/decompression tool (brotlicffi backend)",
        epilog="Example: brotli_tool.py -cf *.txt -rm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--compress", action="store_true", help="Compress files (default if no op specified)")
    group.add_argument("-d", "--decompress", action="store_true", help="Decompress .br files")
    parser.add_argument(
        "-f", "--files", nargs="+", metavar="FILE", help="Files to process (default: recursive current dir)"
    )
    parser.add_argument("-k", "--keep", action="store_true", help="Keep original files (default: remove after success)")
    parser.add_argument(
        "--no-tar", action="store_true", help="Disable tar-based subdir compression (process files individually)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed progress")
    return parser.parse_args()


def find_files_to_process(base_dir: pathlib.Path, recursive: bool = True) -> List[pathlib.Path]:
    files = []
    for p in base_dir.iterdir():
        if p.is_file() and (not p.name.endswith(".br")) and (not p.name.startswith(".")):
            files.append(p)
        elif p.is_dir() and recursive and (p.name != "__pycache__"):
            files.extend(find_files_to_process(p, recursive))
    return sorted(files)


def compress_file_chunked(src: pathlib.Path, dst: pathlib.Path, verbose: bool = False) -> bool:
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(src, "rb") as f_in:
            with open(dst, "wb") as f_out:
                compressor = brotli.Compressor()
                while True:
                    chunk = f_in.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    compressed = compressor.process(chunk)
                    f_out.write(compressed)
                final = compressor.finish()
                f_out.write(final)
        if dst.stat().st_size == 0:
            dst.unlink()
            return False
        return True
    except Exception as e:
        if dst.exists():
            dst.unlink()
        if verbose:
            print(f"❌ Compression failed for {src}: {e}", file=sys.stderr)
        return False


def decompress_file_chunked(src: pathlib.Path, dst: pathlib.Path, verbose: bool = False) -> bool:
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(src, "rb") as f_in:
            with open(dst, "wb") as f_out:
                decompressor = brotli.Decompressor()
                while True:
                    chunk = f_in.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    decompressed = decompressor.decompress(chunk)
                    f_out.write(decompressed)
                final = decompressor.decompress(b"")
                if final:
                    f_out.write(final)
        if dst.stat().st_size == 0:
            dst.unlink()
            return False
        return True
    except Exception as e:
        if dst.exists():
            dst.unlink()
        if verbose:
            print(f"❌ Decompression failed for {src}: {e}", file=sys.stderr)
        return False


@contextmanager
def temp_tar_compression(files: List[pathlib.Path], out_dir: pathlib.Path, verbose: bool = False):
    tar_path = None
    br_path = None
    try:
        tar_path = out_dir / "temp_compressed.tar"
        with tarfile.open(tar_path, "w") as tar:
            for f in files:
                tar.add(f, arcname=f.name)
        br_path = out_dir / f"{tar_path.name}.br"
        if verbose:
            print(f"📦 Compressing {len(files)} files as tar → {br_path.name}")
        if compress_file_chunked(tar_path, br_path, verbose):
            yield br_path
        else:
            yield None
    finally:
        for p in [tar_path, br_path]:
            if p and p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass


def process_directory(base_dir: pathlib.Path, compress: bool, keep: bool, no_tar: bool, verbose: bool = False) -> int:
    success_count = 0
    total_files = 0
    files = find_files_to_process(base_dir)
    if not files:
        if verbose:
            print("ℹ️  No files to process in current directory")
        return 0
    subdirs = [d for d in base_dir.iterdir() if d.is_dir() and (not d.name.startswith("."))]
    if subdirs and (not no_tar):
        for subdir in subdirs:
            subdir_files = find_files_to_process(subdir, recursive=False)
            if subdir_files:
                total_files += len(subdir_files)
                with temp_tar_compression(subdir_files, base_dir, verbose) as br_file:
                    if br_file and br_file.exists():
                        success_count += 1
                        if not keep:
                            for f in subdir_files:
                                if f.exists():
                                    f.unlink()
                            if verbose:
                                print(f"✅ Compressed subdir '{subdir.name}' → {br_file.name}")
                    elif verbose:
                        print(f"⚠️  Skipping subdir '{subdir.name}' (compression failed)")
    for f in files:
        total_files += 1
        if compress:
            src = f
            dst = f.with_suffix(f.suffix + ".br")
            if verbose:
                print(f"📦 Compressing {src.name} → {dst.name}")
            if compress_file_chunked(src, dst, verbose):
                success_count += 1
                if not keep:
                    src.unlink()
            elif verbose:
                print(f"⚠️  Skipping {src.name} (compression failed)")
        else:
            if not f.name.endswith(".br"):
                continue
            src = f
            dst = src.with_suffix("")
            if verbose:
                print(f"📦 Decompressing {src.name} → {dst.name}")
            if decompress_file_chunked(src, dst, verbose):
                success_count += 1
                if not keep:
                    src.unlink()
            elif verbose:
                print(f"⚠️  Skipping {src.name} (decompression failed)")
    return success_count


def main():
    args = parse_args()
    compress = args.compress or not args.decompress
    if args.files:
        files = []
        for path in args.files:
            p = pathlib.Path(path)
            if p.exists():
                files.append(p)
            else:
                print(f"⚠️  Warning: File '{path}' not found", file=sys.stderr)
        if not files:
            print("❌ No valid files provided", file=sys.stderr)
            sys.exit(1)
        success = 0
        for f in files:
            if compress:
                dst = f.with_suffix(f.suffix + ".br")
                if f.stat().st_size > LARGE_FILE_THRESHOLD:
                    print(f"📦 Compressing large file: {f.name} ({f.stat().st_size / (1024 * 1024):.1f} MB)")
                if compress_file_chunked(f, dst, args.verbose):
                    success += 1
                    if not args.keep:
                        f.unlink()
                else:
                    print(f"⚠️  Compression failed for {f.name}", file=sys.stderr)
            else:
                if not f.name.endswith(".br"):
                    print(f"⚠️  Skipping non-.br file: {f.name}", file=sys.stderr)
                    continue
                dst = f.with_suffix("")
                if decompress_file_chunked(f, dst, args.verbose):
                    success += 1
                    if not args.keep:
                        f.unlink()
                else:
                    print(f"⚠️  Decompression failed for {f.name}", file=sys.stderr)
        if args.verbose:
            print(f"\n✅ Processed {len(files)} files, {success} successful")
        sys.exit(0 if success == len(files) else 1)
    else:
        base_dir = pathlib.Path(".")
        success = process_directory(base_dir, compress, args.keep, args.no_tar, args.verbose)
        if args.verbose:
            print(f"\n✅ Completed directory processing")
        sys.exit(0 if success >= 0 else 1)


if __name__ == "__main__":
    main()
