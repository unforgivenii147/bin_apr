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

import base64
import io
import os
import sqlite3
import sys
from pathlib import Path

import py7zr


def get_current_folder_name():
    return Path(Path.cwd()).name


def get_user_folder_name(default_name):
    while True:
        user_input = input(f"Enter folder name (default: {default_name}): ").strip()
        if not user_input:
            return default_name
        return user_input


def folder_exists_in_db(cursor, folder_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (folder_name,))
    return cursor.fetchone() is not None


def create_folder_table(cursor, folder_name):
    cursor.execute(
        f'\n        CREATE TABLE IF NOT EXISTS "{folder_name}" (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            filename TEXT NOT NULL,\n            file_contents BLOB,\n            compressed BOOLEAN DEFAULT 0,\n            original_size INTEGER DEFAULT 0,\n            compressed_size INTEGER DEFAULT 0\n        )\n    '
    )


def compress_data(data_bytes):
    if not data_bytes:
        return None
    try:
        buffer = io.BytesIO()
        with py7zr.SevenZipFile(buffer, "w") as archive:
            archive.writestr("content", data_bytes)
        compressed_data = buffer.getvalue()
        return base64.b64encode(compressed_data).decode("ascii")
    except Exception as e:
        print(f"    Compression error: {e!s}")
        return None


def read_file_contents(filepath):
    try:
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        get_size = Path(filepath).stat().st_size
        if get_size > 10 * 1024 * 1024:
            print(f"    Warning: Large file ({get_size / 1024 / 1024:.1f}MB), may take time to compress")
        for encoding in encodings:
            try:
                with Path(filepath).open(encoding=encoding) as f:
                    content = f.read()
                    return {
                        "content": content,
                        "is_binary": False,
                        "original_size": len(content.encode("utf-8", errors="replace")),
                    }
            except (UnicodeDecodeError, UnicodeError):
                continue
        with Path(filepath).open("rb") as f:
            content = f.read()
            return {"content": content, "is_binary": True, "original_size": len(content)}
    except PermissionError:
        error_msg = "[Permission denied - cannot read file]"
        return {"content": error_msg, "is_binary": False, "original_size": len(error_msg)}
    except Exception as e:
        error_msg = f"[Error reading file: {e!s}]"
        return {"content": error_msg, "is_binary": False, "original_size": len(error_msg)}


def get_files_in_current_dir():
    current_dir = Path.cwd()
    files = []
    try:
        for item in sorted(os.listdir(current_dir)):
            item_path = os.path.join(current_dir, item)
            if Path(item_path).is_file():
                get_size = Path(item_path).stat().st_size
                size_str = f"{get_size / 1024:.1f}KB" if get_size < 1024 * 1024 else f"{get_size / 1024 / 1024:.1f}MB"
                print(f"  Processing: {item} ({size_str})")
                file_data = read_file_contents(item_path)
                if file_data["is_binary"]:
                    compressed = compress_data(file_data["content"])
                    if compressed:
                        files.append(
                            {
                                "filename": item,
                                "contents": compressed,
                                "compressed": 1,
                                "original_size": file_data["original_size"],
                                "compressed_size": len(compressed),
                            }
                        )
                        print(
                            f"    ✓ Compressed {file_data['original_size'] / 1024:.1f}KB to {len(compressed) / 1024:.1f}KB"
                        )
                    else:
                        files.append(
                            {
                                "filename": item,
                                "contents": "[Binary file - compression failed]",
                                "compressed": 0,
                                "original_size": file_data["original_size"],
                                "compressed_size": 0,
                            }
                        )
                else:
                    files.append(
                        {
                            "filename": item,
                            "contents": file_data["content"],
                            "compressed": 0,
                            "original_size": file_data["original_size"],
                            "compressed_size": 0,
                        }
                    )
                    print(f"    ✓ Stored as text ({file_data['original_size'] / 1024:.1f}KB)")
    except PermissionError:
        print("Warning: Permission denied accessing some files")
    return files


def insert_files(cursor, folder_name, files):
    for file_info in files:
        cursor.execute(
            f'\n            INSERT INTO "{folder_name}" (filename, file_contents, compressed, original_size, compressed_size)\n            VALUES (?, ?, ?, ?, ?)\n        ',
            (
                file_info["filename"],
                file_info["contents"],
                file_info.get("compressed", 0),
                file_info.get("original_size", 0),
                file_info.get("compressed_size", 0),
            ),
        )


def main():
    try:
        pass
    except ImportError:
        print("Error: py7zr library is not installed.")
        print("Install it with: pip install py7zr")
        sys.exit(1)
    db_path = "/sdcard/pkgs.db"
    if not os.access("/sdcard/", os.W_OK):
        print("Error: Cannot write to /sdcard/. Make sure you have proper permissions.")
        print("On Android, you might need to:")
        print("1. Grant storage permissions to Termux/terminal app")
        print("2. Or run the script with appropriate permissions")
        sys.exit(1)
    default_name = get_current_folder_name()
    folder_name = get_user_folder_name(default_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    while folder_exists_in_db(cursor, folder_name):
        print(f"Folder name '{folder_name}' already exists in database!")
        folder_name = input("Please enter a different name: ").strip()
        if not folder_name:
            folder_name = default_name + "_new"
            print(f"Using '{folder_name}' as default")
    create_folder_table(cursor, folder_name)
    print(f"\nScanning current directory: {Path.cwd()}")
    print("Reading and compressing file contents...")
    files = get_files_in_current_dir()
    if not files:
        print("No files found in current directory!")
    else:
        insert_files(cursor, folder_name, files)
        conn.commit()
        total_original = sum((f.get("original_size", 0) for f in files))
        total_compressed = sum((f.get("compressed_size", 0) for f in files))
        print(f"\n✅ Successfully added {len(files)} files to table '{folder_name}'")
        if total_compressed > 0:
            ratio = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
            print("📊 Storage stats:")
            print(f"   Original size: {total_original / 1024 / 1024:.2f}MB")
            print(f"   Compressed size: {total_compressed / 1024 / 1024:.2f}MB")
            print(f"   Compression ratio: {ratio:.1f}% saved")
        else:
            print(f"   Total size: {total_original / 1024 / 1024:.2f}MB")
    conn.close()


if __name__ == "__main__":
    main()
