#!/data/data/com.termux/files/usr/bin/python
import operator
import os
import sys
from collections import defaultdict
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display


def scan_directory(path="."):
    """
    Scans the given directory to gather information about files and subdirectories.
    """
    total_size = 0
    file_count = 0
    folder_count = 0
    extensions = set()
    size_by_ext = defaultdict(int)

    for root, dirs, files in os.walk(path):
        folder_count += len(dirs)
        for filename in files:
            file_count += 1
            full_path = Path(root) / filename
            try:
                size = full_path.stat().st_size
            except OSError:
                size = 0
            total_size += size
            ext = full_path.suffix
            ext = ext.lower() if ext else "(no extension)"
            extensions.add(ext)
            size_by_ext[ext] += size
    return (
        total_size,
        file_count,
        folder_count,
        extensions,
        size_by_ext,
    )


def format_size(size_in_bytes):
    """Formats size in bytes to a more human-readable format."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_in_bytes / 1024**3:.2f} GB"


def write_summary(filename: Path | None = None) -> None:
    """
    Writes a summary of directory information to a file or to stderr.
    """
    (
        total_size,
        file_count,
        folder_count,
        extensions,
        size_by_ext,
    ) = scan_directory()

    # Prepare the summary string
    summary_lines = []
    summary_lines.append(f"Total size: {format_size(total_size)}\n")
    summary_lines.append("File extensions:\n")
    sorted_extensions = sorted(list(extensions))
    for ext in sorted_extensions:
        summary_lines.append(f"   - {ext}\n")
    summary_lines.append(f"Number of files: {file_count}\n")
    summary_lines.append(f"Number of folders: {folder_count}\n")
    summary_lines.append("Size by extension:\n")

    sorted_size_by_ext = sorted(size_by_ext.items(), key=operator.itemgetter(1), reverse=True)
    for ext, size in sorted_size_by_ext:
        summary_lines.append(f"  {ext}: {format_size(size)}\n")
        # Also print to stderr if not saving to file
        if filename is None or filename == sys.stderr:
            print(f"  {ext}: {format_size(size)}\n", file=sys.stderr)

    summary_string = "".join(summary_lines)

    if filename and filename != sys.stderr:
        try:
            with filename.open("w", encoding="utf-8") as f:
                f.write(summary_string)
            print(f"Summary saved to {filename}")
        except IOError as e:
            print(f"Error saving summary to {filename}: {e}", file=sys.stderr)
    elif filename is None:
        # If no filename provided and not defaulting to stderr, just print to stdout
        print(summary_string)
    # If filename is sys.stderr, it's already printed above


def create_bar_chart(chart_type: str, output_filename: str | None = None) -> None:
    """
    Creates and optionally saves a Matplotlib bar chart of file sizes by extension.
    """
    (_, _, _, _, size_by_ext) = scan_directory()

    # Filter out entries with zero size and sort by size in descending order
    sorted_items = sorted(
        [(ext, size) for ext, size in size_by_ext.items() if size > 0], key=operator.itemgetter(1), reverse=True
    )

    if not sorted_items:
        print("No data to plot.", file=sys.stderr)
        return

    extensions, sizes = zip(*sorted_items)

    # Prepare Persian text for labels if needed
    if chart_type == "persian":
        reshaped_extensions = [arabic_reshaper.reshape(get_display(ext)) for ext in extensions]
        title = arabic_reshaper.reshape(get_display("اندازه بر اساس پسوند فایل"))
        plt.title(title)
        plt.xticks(rotation=45, ha="right")  # Adjust rotation for better readability
        plt.gca().set_xticklabels(reshaped_extensions)
    else:
        # For English or other languages, use original extensions
        reshaped_extensions = extensions
        plt.title("Size by File Extension")
        plt.xticks(rotation=45, ha="right")  # Rotate labels for better readability
        plt.gca().set_xticklabels(reshaped_extensions)

    plt.figure(figsize=(12, 7))
    plt.bar(reshaped_extensions, sizes, color="skyblue")
    plt.xlabel("File Extension")
    plt.ylabel("Size (bytes)")
    plt.tight_layout()

    if output_filename:
        try:
            plt.savefig(output_filename)
            print(f"Bar chart saved to {output_filename}")
        except Exception as e:
            print(f"Error saving chart to {output_filename}: {e}", file=sys.stderr)
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze directory information.")
    parser.add_argument(
        "-s", "--save", action="store_true", help="Save the report to a file named .dirinfo in the current directory."
    )
    parser.add_argument(
        "-i",
        "--image",
        metavar="FILENAME",
        type=str,
        help="Save a Matplotlib bar chart of file types and sizes to the specified image file (e.g., chart.png).",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=["persian", "english"],
        default="english",
        help="Specify the language/type of the Matplotlib chart title and labels (default: english).",
    )
    # Add an argument to specify the directory to scan, defaulting to current directory
    parser.add_argument(
        "path",
        metavar="PATH",
        type=str,
        nargs="?",
        default=".",
        help="The directory to scan (default: current directory).",
    )

    args = parser.parse_args()

    if args.save:
        # If -s is used, save to .dirinfo file
        write_summary(Path(".dirinfo"))
    elif args.image:
        # If -i is used, create and save the chart
        create_bar_chart(args.type, args.image)
    else:
        # Default behavior: print summary to stdout
        write_summary()  # Writes to stdout when filename is None
