#!/data/data/com.termux/files/usr/bin/python
import operator
import os
import shutil
from pathlib import Path
from dh import unique_path, get_files
from loguru import logger


def get_all_files(cwd):
    files = []
    for path in get_files(cwd):
        if path.is_file():
            size = path.stat().st_size
            files.append((path, size))
    return sorted(files, key=operator.itemgetter(1))


def calculate_optimal_folders(files):
    if len(files) < 2:
        return 1
    sizes = [size for _, size in files]
    max_size, min_size = max(sizes), min(sizes)
    range_size = max_size - min_size
    target_range_per_folder = range_size / 100
    num_folders = max(
        1,
        int(range_size / target_range_per_folder),
    )
    return min(num_folders, len(files))


def create_range_folders(cwd, files, num_folders):
    sizes = sorted([size for _, size in files])
    folder_ranges = []
    files_per_folder = len(files) // num_folders
    remainder = len(files) % num_folders
    start_idx = 0
    for i in range(num_folders):
        end_idx = start_idx + files_per_folder + (1 if i < remainder else 0)
        folder_files = sizes[start_idx:end_idx]
        if folder_files:
            min_size, max_size = min(folder_files), max(folder_files)

            def fsz(size):
                if size < 1000:
                    return f"{size}B"
                if size < 1_000_000:
                    return f"{size // 1000}k"
                if size < 1_000_000_000:
                    return f"{size // 1_000_000}M"
                return f"{size // 1_000_000_000}G"

            folder_name = f"{fsz(min_size)}-{fsz(max_size)}"
            folder_ranges.append((min_size, max_size, folder_name))
            folder_path = os.path.join(cwd, folder_name)
            Path(folder_path).mkdir(exist_ok=True, parents=True)
        start_idx = end_idx
    return folder_ranges


def distribute_files(files, folders, cwd):
    size_to_folder = {}
    for (
        min_size,
        max_size,
        folder_name,
    ) in folders:
        size_to_folder[min_size, max_size] = folder_name
    moved_count = 0
    for filepath, size in files:
        for (
            min_size,
            max_size,
        ), folder_name in size_to_folder.items():
            if min_size <= size <= max_size:
                dest_folder = os.path.join(cwd, folder_name)
                dest_path = os.path.join(
                    dest_folder,
                    Path(filepath).name,
                )
                try:
                    dest_path = unique_path(dest_path)
                    shutil.move(filepath, dest_path)
                    moved_count += 1
                    break
                except Exception as e:
                    logger.info(f"Failed to move {filepath}: {e}")
                break
        else:
            logger.info(f"No folder match for {Path(filepath).name} ({size:,} bytes)")


def main():
    cwd = Path.cwd()
    files = get_all_files(cwd)
    if not files:
        logger.info("No files found.")
        return
    num_folders = 4
    folders = create_range_folders(cwd, files, num_folders)
    distribute_files(files, folders, cwd)
    logger.info("Folderization complete!")


if __name__ == "__main__":
    main()
