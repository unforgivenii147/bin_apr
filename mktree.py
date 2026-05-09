#!/data/data/com.termux/files/usr/bin/python
import os
import re
import sys
from pathlib import Path

from loguru import logger


def parse_tree_file(tree_path):
    """
    Parse a tree diagram text file and return a nested structure.
    Returns a list of tuples: (path_parts, is_file)
    """
    with Path(tree_path).open("r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines if line.strip()]
    # e.g., "dictionary-webapp/", or lines starting with '├──'/'└──'/'│'
    # We assume the first line is the root directory (e.g., "dictionary-webapp/")
    root_line = lines[0].strip() if lines else ""
    root_name = re.sub(r"[├└│─]+", "", root_line).strip().rstrip("/")
    root_parts = [root_name] if root_name else []
    entries = []
    stack = [(0, root_parts)]  # (indent_level, path_parts)
    for line in lines[1:]:
        if not line.strip():
            continue
        # We'll use a robust regex to extract the name and detect indentation level
        match = re.match(r"^([├└│ ]*)([├└]──\s*)?(\S.*)$", line)
        if not match:
            continue  # Skip malformed lines
        prefix, _marker, name = match.groups()
        name = name.strip()
        if name.startswith("#") or name == "":
            continue
        # But since tree uses │ and spaces, we can count spaces + │ characters
        # Simplified: count number of '│ ' or '   ' in prefix
        # Better: use number of leading spaces (approx 4 per level)
        # Let's use the number of leading spaces as a proxy for depth
        indent = len(prefix) // 4  # assuming 4-space indentation per level
        while stack and stack[-1][0] >= indent:
            stack.pop()
        current_path = stack[-1][1] if stack else []
        # Heuristics: ends with '/' or no extension (common for dirs), but safer:
        # - If the next non-empty line has higher indent, it's a dir
        # - Else, it's a file
        # For simplicity, we assume: if name contains '/', treat as directory
        # Otherwise, we treat it as a file unless explicitly marked with '/'.
        is_dir = name.endswith("/") or "." not in Path(name).name or any(c in name for c in ["/", "\\"])
        name = name.rstrip("/")
        full_path = [*current_path, name]
        entries.append((indent, full_path, is_dir))
        if is_dir:
            stack.append((indent, full_path))
    return entries


def create_tree_from_entries(entries):
    """Create actual folders and files from parsed entries."""
    created_dirs = set()
    for _indent, path_parts, is_dir in entries:
        # Skip root (first entry, usually just the project name)
        if len(path_parts) == 1 and path_parts[0] == "dictionary-webapp":
            continue
        path = Path(*path_parts)
        if is_dir:
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.add(str(path))
        else:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            # Create empty file
            path.touch()


def main():
    tree_file = sys.argv[1]
    if not Path(tree_file).exists():
        print(f"❌ Error: '{tree_file}' not found in current directory.")
        return
    print(f"📖 Parsing '{tree_file}'...")
    entries = parse_tree_file(tree_file)
    if not entries:
        print("⚠️  No valid entries found in tree file.")
        return
    print(f"✅ Parsed {len(entries)} entries.")
    print("📁 Creating folder structure...")
    create_tree_from_entries(entries)
    print("✨ Done! Folder structure created successfully.")


if __name__ == "__main__":
    main()
