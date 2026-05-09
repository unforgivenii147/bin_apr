#!/data/data/com.termux/files/usr/bin/python
import base64
import io
import os
import sqlite3
import sys
from pathlib import Path

import py7zr
from loguru import logger


def get_current_folder_name():
    return Path(Path.cwd()).name


def get_user_folder_name(default_name):
    while True:
        user_input = input(f"Enter folder name (default: {default_name}): ").strip()
        if not user_input:
            return default_name
        return user_input


def folder_exists_in_db(cursor, folder_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (folder_name,),
    )
    return cursor.fetchone() is not None


def create_folder_table(cursor, folder_name):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{folder_name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_contents BLOB,
            compressed BOOLEAN DEFAULT 0,
            original_size INTEGER DEFAULT 0,
            compressed_size INTEGER DEFAULT 0
        )
    """)


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
        logger.info(f"    Compression error: {e!s}")
        return None


def read_file_contents(filepath):
    try:
        encodings = [
            "utf-8",
            "latin-1",
            "cp1252",
            "iso-8859-1",
        ]
        get_size = Path(filepath).stat().st_size
        if get_size > 10 * 1024 * 1024:
            logger.info(f"    Warning: Large file ({get_size / 1024 / 1024:.1f}MB), may take time to compress")
        for encoding in encodings:
            try:
                with Path(filepath).open(encoding=encoding) as f:
                    content = f.read()
                    return {
                        "content": content,
                        "is_binary": False,
                        "original_size": len(
                            content.encode(
                                "utf-8",
                                errors="replace",
                            )
                        ),
                    }
            except (
                UnicodeDecodeError,
                UnicodeError,
            ):
                continue
        with Path(filepath).open("rb") as f:
            content = f.read()
            return {
                "content": content,
                "is_binary": True,
                "original_size": len(content),
            }
    except PermissionError:
        error_msg = "[Permission denied - cannot read file]"
        return {
            "content": error_msg,
            "is_binary": False,
            "original_size": len(error_msg),
        }
    except Exception as e:
        error_msg = f"[Error reading file: {e!s}]"
        return {
            "content": error_msg,
            "is_binary": False,
            "original_size": len(error_msg),
        }


def get_files_in_current_dir():
    current_dir = Path.cwd()
    files = []
    try:
        for item in sorted(os.listdir(current_dir)):
            item_path = os.path.join(current_dir, item)
            if Path(item_path).is_file():
                get_size = Path(item_path).stat().st_size
                size_str = f"{get_size / 1024:.1f}KB" if get_size < 1024 * 1024 else f"{get_size / 1024 / 1024:.1f}MB"
                logger.info(f"  Processing: {item} ({size_str})")
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
                        logger.info(
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
                    logger.info(f"    ✓ Stored as text ({file_data['original_size'] / 1024:.1f}KB)")
    except PermissionError:
        logger.info("Warning: Permission denied accessing some files")
    return files


def insert_files(cursor, folder_name, files):
    for file_info in files:
        cursor.execute(
            f"""
            INSERT INTO "{folder_name}" (filename, file_contents, compressed, original_size, compressed_size)
            VALUES (?, ?, ?, ?, ?)
        """,
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
        logger.info("Error: py7zr library is not installed.")
        logger.info("Install it with: pip install py7zr")
        sys.exit(1)
    db_path = "/sdcard/pkgs.db"
    if not os.access("/sdcard/", os.W_OK):
        logger.info("Error: Cannot write to /sdcard/. Make sure you have proper permissions.")
        logger.info("On Android, you might need to:")
        logger.info("1. Grant storage permissions to Termux/terminal app")
        logger.info("2. Or run the script with appropriate permissions")
        sys.exit(1)
    default_name = get_current_folder_name()
    folder_name = get_user_folder_name(default_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    while folder_exists_in_db(cursor, folder_name):
        logger.info(f"Folder name '{folder_name}' already exists in database!")
        folder_name = input("Please enter a different name: ").strip()
        if not folder_name:
            folder_name = default_name + "_new"
            logger.info(f"Using '{folder_name}' as default")
    create_folder_table(cursor, folder_name)
    logger.info(f"\nScanning current directory: {Path.cwd()}")
    logger.info("Reading and compressing file contents...")
    files = get_files_in_current_dir()
    if not files:
        logger.info("No files found in current directory!")
    else:
        insert_files(cursor, folder_name, files)
        conn.commit()
        total_original = sum(f.get("original_size", 0) for f in files)
        total_compressed = sum(f.get("compressed_size", 0) for f in files)
        logger.info(f"\n✅ Successfully added {len(files)} files to table '{folder_name}'")
        if total_compressed > 0:
            ratio = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
            logger.info("📊 Storage stats:")
            logger.info(f"   Original size: {total_original / 1024 / 1024:.2f}MB")
            logger.info(f"   Compressed size: {total_compressed / 1024 / 1024:.2f}MB")
            logger.info(f"   Compression ratio: {ratio:.1f}% saved")
        else:
            logger.info(f"   Total size: {total_original / 1024 / 1024:.2f}MB")
    conn.close()


if __name__ == "__main__":
    main()
