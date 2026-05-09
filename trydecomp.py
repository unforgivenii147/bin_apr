#!/data/data/com.termux/files/usr/bin/python
import bz2
import gzip
import lzma
import pickle
import sys
import tarfile
import zipfile
import zlib
from pathlib import Path

from loguru import logger

try:
    import brotli
except ImportError:
    brotli = None
try:
    import zstandard

    zstd_available = True
except ImportError:
    zstd_available = False
try:
    import py7zr
except ImportError:
    py7zr = None


def try_decompress(filename):
    logger.info(f"Attempting to decompress: {filename}\n")
    compression_methods = {
        "zlib": zlib.decompress,
        "bz2": bz2.decompress,
        "gzip": gzip.decompress,
        "lzma": lzma.decompress,
        "pickle": pickle.loads,
    }
    if brotli:
        compression_methods["brotli"] = brotli.decompress
    if zstd_available:

        def zstd_decompress_all(data):
            try:
                dctx = zstandard.ZstdDecompressor()
                return dctx.decompress(data)
            except zstandard.ZstdError as e:
                msg = f"Zstandard decompression error: {e}"
                raise ValueError(msg) from e

        compression_methods["zstandard"] = zstd_decompress_all
    if py7zr:
        pass
    try:
        file_data = Path(filename).read_bytes()
    except FileNotFoundError:
        logger.info(f"Error: File not found at {filename}\n")
        return
    except Exception as e:
        logger.info(f"Error reading file {filename}: {e}\n")
        return
    success = False
    for name, func in compression_methods.items():
        try:
            logger.info(f"Trying {name}...")
            decompressed_data = func(file_data)
            if decompressed_data and len(decompressed_data) < len(file_data) * 10:
                logger.info(f"  SUCCESS: Decompressed using {name}. Size: {len(decompressed_data)} bytes.\n")
                success = True
            else:
                logger.info(
                    f"  FAILED: {name} did not yield valid decompressed data (size: {len(decompressed_data)}).\n"
                )
        except Exception as e:
            logger.info(f"  FAILED: {name} raised an exception: {type(e).__name__}: {e}\n")
    if tarfile.is_tarfile(filename):
        try:
            logger.info("Trying tarfile...")
            with tarfile.open(filename, "r") as tar:
                members = tar.getmembers()
                if members:
                    logger.info(
                        f"  SUCCESS: Opened as tar archive with {len(members)} members. First member: {members[0].name}\n"
                    )
                    success = True
                else:
                    logger.info("  FAILED: tarfile is empty.\n")
        except Exception as e:
            logger.info(f"  FAILED: tarfile opened with exception: {type(e).__name__}: {e}\n")
    if zipfile.is_zipfile(filename):
        try:
            logger.info("Trying zipfile...")
            with zipfile.ZipFile(filename, "r") as zip_ref:
                file_list = zip_ref.namelist()
                if file_list:
                    logger.info(
                        f"  SUCCESS: Opened as zip archive with {len(file_list)} files. First file: {file_list[0]}\n"
                    )
                    success = True
                else:
                    logger.info("  FAILED: zipfile is empty.\n")
        except Exception as e:
            logger.info(f"  FAILED: zipfile opened with exception: {type(e).__name__}: {e}\n")
    if py7zr:
        try:
            logger.info("Trying py7zr (7z archive)...")
            with py7zr.SevenZipFile(filename, mode="r") as z:
                file_list = z.getnames()
                if file_list:
                    logger.info(
                        f"  SUCCESS: Opened as 7z archive with {len(file_list)} files. First file: {file_list[0]}\n"
                    )
                    success = True
                else:
                    logger.info("  FAILED: py7zr archive is empty.\n")
        except Exception as e:
            logger.info(f"  FAILED: py7zr opened with exception: {type(e).__name__}: {e}\n")
    if not success:
        logger.info("No compression or archive format was successfully identified and decompressed.\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.info("Usage: python your_script_name.py <filename>\n")
        sys.exit(1)
    input_filename = sys.argv[1]
    try_decompress(input_filename)
