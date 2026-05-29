#!/data/data/com.termux/files/usr/bin/python

import asyncio
import contextlib
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
        with compressed_path.open("rb") as f:
            f.write(compressed_data)
        compressed_size = compressed_path.stat().st_size
        if not compressed_size:
            print(f"Compressed file empty: {compressed_path}")
            return False
        path.unlink()
        reduction = (original_size - compressed_size) / original_size * 100
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
                shutil.rmtree(dir_path)
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
