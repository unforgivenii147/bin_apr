#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
import multiprocessing
import sys
from pathlib import Path
from dh import runcmd

# --- Configuration ---
# Directory to start searching for TTF files ('.' means current directory)
SEARCH_DIR = Path.cwd()
# --- End Configuration ---


def check_app():
    """Checks if woff2_compress command is available in PATH."""
    try:
        # Use subprocess.run with check=True to raise CalledProcessError if command not found
        runcmd(["woff2_compress"], show_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: 'woff2_compress' command not found.")
        print("Please install 'woff2tools' (e.g., 'sudo apt-get install woff2tools').")
        return False


def convert_ttf_to_woff2(ttf_path: Path) -> tuple[str, bool, str]:
    """
    Converts a single TTF file to WOFF2 using woff2_compress.
    Returns a tuple: (original_ttf_path, success_status, message)
    """
    if not ttf_path.is_file():
        return str(ttf_path), False, "Path is not a file."

    success = False
    message = ""
    woff2_path = ttf_path.with_suffix(".woff2")

    command = ["woff2_compress", str(ttf_path.name)]

    try:
        print(f"Converting: {ttf_path} -> {woff2_path}")
        # Run the command, capture output and errors
        ret, txt, err = runcmd(command, show_output=True)
        if ret:
            print(txt)
            print(err)
            return
        sz = woff2_path.stat().st_size
        if not sz:
            return
        success = True
        message = f"{ttf_path.name}"
        print(message, end=" ")

        try:
            os.remove(ttf_path)
        except OSError as e:
            message += f" | Error deleting {ttf_path}: {e}"
            success = False  # Mark as failed if deletion fails after successful conversion

    except FileNotFoundError:
        message = f"Error: 'woff2_compress' command not found. Please install it."
        # No need to try deleting if command itself is missing
    except subprocess.CalledProcessError as e:
        message = (
            f"Error converting {ttf_path.name}: Command '{' '.join(e.cmd)}' failed with exit code {e.returncode}.\n"
        )
        message += f"Stderr: {e.stderr.strip()}"
        message += f"\nStdout: {e.stdout.strip()}"
        # Do NOT delete original TTF if an error occurred
    except Exception as e:
        message = f"An unexpected error occurred for {ttf_path.name}: {e}"
        # Do NOT delete original TTF if an error occurred

    return str(ttf_path), success, message


def find_ttf_files(directory: str) -> list[Path]:
    """Recursively finds all .ttf files in the given directory."""
    ttf_files = []
    base_path = Path(directory)
    for item in base_path.glob("*.ttf"):
        if item.is_file():
            ttf_files.append(item)
    return ttf_files


def main():
    if not check_app():
        sys.exit(1)
    print(f"Searching for TTF files in '{os.path.abspath(SEARCH_DIR)}' and subdirectories...")
    ttf_files_to_process = find_ttf_files(SEARCH_DIR)

    if not ttf_files_to_process:
        print("No .ttf files found. Exiting.")
        sys.exit(0)

    print(f"Found {len(ttf_files_to_process)} TTF files. Starting conversion...")

    # Use multiprocessing.Pool for parallel conversion
    # You can adjust the number of processes (e.g., processes=4)
    # If None, it defaults to os.cpu_count()
    num_processes = multiprocessing.cpu_count()
    print(f"Using {num_processes} parallel processes.")

    results = []
    # Use starmap to pass arguments to convert_ttf_to_woff2
    # We need to convert Path objects to strings for the pool function if it expects strings,
    # but here convert_ttf_to_woff2 directly accepts Path.
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Prepare arguments for starmap: each item in the iterable should be a tuple of arguments.
        # Here, we only need to pass the Path object for each file.
        results = pool.starmap(convert_ttf_to_woff2, [(ttf_file,) for ttf_file in ttf_files_to_process])

    # Process results
    successful_conversions = 0
    failed_conversions = 0
    for ttf_path, success, message in results:
        if success:
            successful_conversions += 1
        else:
            failed_conversions += 1
            print(f"Processing failed for {ttf_path}: {message}")

    print("\n--- Conversion Summary ---")
    print(f"Total TTF files processed: {len(ttf_files_to_process)}")
    print(f"Successfully converted: {successful_conversions}")
    print(f"Failed conversions (original TTF not deleted): {failed_conversions}")
    print("--------------------------")


if __name__ == "__main__":
    main()
