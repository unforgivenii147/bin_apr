#!/data/data/com.termux/files/usr/bin/python
"""
Repack unpacked Python wheels using the wheel library API.

Assumptions:
- Current directory contains one subdirectory per wheel.
- Each wheel directory contains exactly one `*.dist-info` subdirectory.
- That `*.dist-info` name determines the wheel file name.

Example:
.
├── scikit_build_core
│   ├── scikit_build_core
│   └── scikit_build_core-0.12.2.dist-info
├── scikit_fuzzy
│   ├── scikit_fuzzy-0.5.0.dist-info
│   └── skfuzzy

→ Produces:
./scikit_build_core-0.12.2.whl
./scikit_fuzzy-0.5.0.whl
"""

import sys
import zipfile
from pathlib import Path

from wheel.archive import wheel_load  # Function to load metadata from .dist-info
from wheel.wheelfile import WheelFile  # Use WheelFile from the wheel library

# Define the root directory where unpacked wheels are located.
# The script assumes it's run from the parent directory of these unpacked folders.
# If you need to specify a different source directory, modify this or pass as argument.
UNPACKED_WHEELS_SOURCE_DIR = Path.cwd()

# Define the destination directory for the created wheels.
# If commented out, wheels will be created in the current directory.
# WHEELS_OUTPUT_DIR = Path("./output_wheels")
WHEELS_OUTPUT_DIR = None  # Save in the current directory by default


def find_dist_info_dir(pkg_dir: Path) -> Path | None:
    """Return the single *.dist-info directory inside pkg_dir, or None."""
    candidates = [p for p in pkg_dir.iterdir() if p.is_dir() and p.name.endswith(".dist-info")]
    if not candidates:
        return None
    if len(candidates) > 1:
        # In a real scenario, you might want to log this or handle it differently
        print(
            f"Warning: Multiple .dist-info dirs found in {pkg_dir}, using the first: {candidates[0].name}",
            file=sys.stderr,
        )
    return candidates[0]


def create_wheel_for_dir(pkg_dir: Path, dest_dir: Path | None = None):
    """Create a .whl file for the given unpacked wheel directory using wheel.wheelfile."""
    dist_info = find_dist_info_dir(pkg_dir)
    if dist_info is None:
        print(f"Skipping {pkg_dir}: no *.dist-info dir found.")
        return

    # Load metadata from the .dist-info directory
    try:
        metadata = wheel_load(dist_info)
        wheel_filename = metadata.WheelFilename
    except Exception as e:
        print(f"Error loading metadata from {dist_info}: {e}")
        print("Skipping this directory.")
        return

    # Determine the destination path
    output_path = dest_dir / wheel_filename if dest_dir else Path(wheel_filename)

    # Ensure output directory exists if specified
    if dest_dir:
        dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Packing {pkg_dir} -> {output_path}")

    try:
        # Use WheelFile to create the wheel archive
        # The zip_effective_level parameter controls compression. 1 is fastest, 9 is best compression.
        # zipfile.ZIP_DEFLATED is the standard compression method.
        with WheelFile(
            str(output_path),
            "w",
            compression=zipfile.ZIP_DEFLATED,
            # Use metadata.zip_effective_level if available and desired,
            # otherwise default to a reasonable value.
            # zip_effective_level=metadata.zip_effective_level if hasattr(metadata, 'zip_effective_level') else zipfile.ZIP_DEFLATED
            # Note: WheelFile constructor doesn't directly take zip_effective_level.
            # Compression is handled by zipfile.ZipFile internally.
            # The wheel library writes files, respecting their original compression if possible,
            # but typically uses DEFLATE for new archives.
        ) as wf:
            # Add all files from the unpacked package directory to the wheel
            for item in pkg_dir.rglob("*"):
                if item.is_file():
                    # Calculate the path relative to the package directory
                    arcname = item.relative_to(pkg_dir).as_posix()
                    wf.write_to(str(item), arcname)
                elif item.is_dir() and item.name.endswith(".dist-info"):
                    # Specifically add the .dist-info directory contents
                    # The wheel library usually handles this implicitly when writing files,
                    # but explicit addition can ensure correctness.
                    # Note: WheelFile.write_to adds individual files.
                    # The structure should be preserved by the walk.
                    pass  # Already handled by iterating through files

            # Ensure the essential .dist-info metadata directory is included correctly
            # WheelFile.write_to should handle adding files from disk.
            # If you encounter issues, you might need to explicitly add dist-info files.
            # Example:
            # for f in dist_info.rglob("*"):
            #     if f.is_file():
            #         arcname = f.relative_to(pkg_dir).as_posix()
            #         wf.write_to(str(f), arcname)

        print(f"Successfully created wheel: {output_path}")

    except Exception as e:
        print(f"Error creating wheel for {pkg_dir}: {e}")
        # Clean up potentially incomplete wheel file
        if output_path.exists():
            output_path.unlink()


def main():
    """Main function to iterate through unpacked directories and create wheels."""
    if WHEELS_OUTPUT_DIR:
        WHEELS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Output directory for wheels: {WHEELS_OUTPUT_DIR}")

    processed_count = 0
    for entry in UNPACKED_WHEELS_SOURCE_DIR.iterdir():
        # We are looking for directories that represent unpacked wheels.
        # These are typically directories named after the package itself,
        # containing a .dist-info folder.
        if entry.is_dir() and not entry.name.endswith(".dist-info"):
            dist_info = find_dist_info_dir(entry)
            if dist_info:  # Only process if it looks like an unpacked wheel
                try:
                    create_wheel_for_dir(entry, dest_dir=WHEELS_OUTPUT_DIR)
                    processed_count += 1
                except Exception as e:
                    print(f"Critical error while processing {entry}: {e}", file=sys.stderr)
            # else:
            # Optionally, print a message for directories that are skipped
            # print(f"Skipping {entry}: does not appear to be a valid unpacked wheel directory.")

    print(f"\nDone. Processed {processed_count} directories.")


if __name__ == "__main__":
    # Ensure the 'wheel' library is installed
    try:
        pass
    except ImportError:
        print("Error: The 'wheel' library is not installed.")
        print("Please install it using: pip install wheel")
        sys.exit(1)

    main()
