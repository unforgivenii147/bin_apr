#!/data/data/com.termux/files/usr/bin/python
"""
remove_tag.py
Removes a specific HTML tag (provided via command line) from all .html files
in the current directory and subdirectories.
Usage:
    python remove_tag.py tagname
Example:
    python remove_tag.py script
"""

import os
import sys
from bs4 import BeautifulSoup


def remove_tag_from_html_file(file_path, tag_name):
    """Remove all occurrences of tag_name from a given HTML file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        # Find and decompose all instances of tag_name
        for tag in soup.find_all(tag_name):
            tag.decompose()
        # Write back cleaned HTML
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"✅ Removed <{tag_name}> from {file_path}")
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")


def process_directory(root_dir, tag_name):
    """Recursively process all .html files in root_dir."""
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(".html"):
                full_path = os.path.join(dirpath, filename)
                remove_tag_from_html_file(full_path, tag_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_tag.py tagname")
        sys.exit(1)
    tag_name = sys.argv[1]
    process_directory(os.getcwd(), tag_name)
