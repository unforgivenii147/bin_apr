#!/data/data/com.termux/files/usr/bin/python
import asyncio
import contextlib
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
import lzma_mt
from loguru import logger

_executor = asyncio.Semaphore(4)  # limit concurrent compressions


def fsz(size: int) -> str:
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
        logger.error(f"Failed to compress folder {folder_path} → {output_base_name}: {e}")
        return False


async def atomic_write_async(data: bytes, final_path: Path) -> bool:
    temp_dir = final_path.parent
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = None
    loop = asyncio.get_running_loop()
    try:

        def _create_temp():
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=temp_dir,
                prefix=".tmp_",
                suffix=".xz",
                delete=False,
            ) as f:
                f.write(data)
                f.flush()
            return Path(f.name)

        temp_path = await loop.run_in_executor(None, _create_temp)
        await loop.run_in_executor(None, lambda: temp_path.rename(final_path))
        logger.debug(f"Atomically written to: {final_path}")
        return True
    except Exception as e:
        logger.error(f"Atomic write failed for {final_path}: {e}")
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass  # best-effort cleanup
        return False


async def safe_delete_async(path: Path, max_retries: int = 3) -> bool:
    loop = asyncio.get_running_loop()
    for attempt in range(max_retries):
        try:
            if not path.exists():
                return True  # already gone

            def _delete():
                if path.is_dir():
                    shutil.rmtree(str(path))
                else:
                    path.unlink()

            await loop.run_in_executor(None, _delete)
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                await asyncio.sleep(0.1 * (attempt + 1))  # exponential backoff
                continue
            logger.error(f"Cannot delete {path} after {max_retries} attempts due to PermissionError")
            return False
        except FileNotFoundError:
            logger.debug(f"File not found during deletion attempt: {path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            return False
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
            return lzma_mt.compress(data, threads=4, preset=9)

        compressed_data = await loop.run_in_executor(None, _compress)
        if not await atomic_write_async(compressed_data, compressed_path):
            return False
        compressed_size = compressed_path.stat().st_size
        if not compressed_size:
            logger.error(f"Compressed file empty: {compressed_path}")
            return False
        if not await safe_delete_async(path):
            logger.warning(f"Failed to delete original after compression: {path}")
            return False
        reduction = ((original_size - compressed_size) / original_size) * 100
        logger.info(f"{path.name}|{fsz(original_size)} → {fsz(compressed_size)} {reduction:.2f}% reduction")
        return True
    except Exception as e:
        logger.error(f"Compression failed for {path}: {e}")
        return False


async def get_files_async(directory: Path) -> list[Path]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, lambda: [p for p in directory.glob("*") if p.is_file() and not p.is_symlink() and should_compress(p)]
    )


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
        for dir_path in dirs_to_compress:
            logger.info(f"compressing {dir_path.relative_to(cwd)}")
            if await compress_folder_async(dir_path, str(dir_path.parent / dir_path.name), format="tar"):
                logger.info(f"compressed {dir_path.relative_to(cwd)}")
                await safe_delete_async(dir_path)
    files_to_compress = await get_files_async(cwd)
    if not files_to_compress:
        logger.info("No files to compress")
        return
    total_original = 0
    total_compressed = 0
    successful = 0
    for i, path in enumerate(files_to_compress, 1):
        logger.info(f"\n[{i}/{len(files_to_compress)}] {path.name}")
        orig_size = path.stat().st_size
        total_original += orig_size
        if await compress_file_async(path):
            successful += 1
        compressed_path = path.with_suffix(path.suffix + ".xz")
        if compressed_path.exists():
            total_compressed += compressed_path.stat().st_size
    if successful > 0:
        savings = total_original - total_compressed
        savings_percent = (savings / total_original) * 100
        logger.info(f"Space saved: {fsz(savings)} {savings_percent:.1f}%")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
