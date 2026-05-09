#!/data/data/com.termux/files/usr/bin/python
"""
Deduplicates top-level function, class, and constant definitions across .py files.
- Scans recursively in current dir
- Uses AST + hash for exact duplicate detection
- Moves duplicates to `utils.py`
- Adds `from utils import X` to affected files
- Creates `.bak` backups of modified files
"""

import ast
import hashlib
import os
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CURRENT_DIR = Path(".")
UTILS_FILE = CURRENT_DIR / "utils.py"
# Nodes considered for deduplication
TOP_LEVEL_NODES = (ast.FunctionDef, ast.ClassDef, ast.Assign)
# Nodes for constants: simple assignments with single target & literal/Name/Constant value
CONSTANT_NODES = (ast.Assign,)


def is_simple_constant(node: ast.Assign) -> bool:
    """Check if assignment is a 'simple constant' (e.g., X = 1, X = 'hello', X = MY_CONST)."""
    if len(node.targets) != 1:
        return False
    target = node.targets[0]
    if not isinstance(target, ast.Name):
        return False
    value = node.value
    if isinstance(value, ast.Constant):
        return True
    elif isinstance(value, ast.Name):
        return True  # e.g., X = MY_OTHER_CONST
    # Optional: allow unary ops like -1, ~x, not y
    elif isinstance(value, ast.UnaryOp) and isinstance(value.operand, (ast.Constant, ast.Name)):
        return True
    return False


def get_name(node: ast.AST) -> str:
    """Get name of function/class or target of assign."""
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        return node.name
    elif isinstance(node, ast.Assign):
        if len(node.targets) > 0 and isinstance(node.targets[0], ast.Name):
            return node.targets[0].id  # ✅ Fixed: use .id
        elif isinstance(node.targets[0], (ast.Tuple, ast.List)):
            # Skip tuple unpacking for simplicity (e.g., x, y = 1, 2)
            return ""
    return ""


def node_to_source(node: ast.AST, source_lines: List[str]) -> str:
    """Extract full source text of node from lines."""
    start_line = node.lineno - 1
    end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start_line + 1
    # Fallback: if end_lineno not available, estimate (less accurate)
    if end_line <= start_line:
        end_line = start_line + 1
    return "\n".join(source_lines[start_line:end_line])


def hash_node(node: ast.AST, source_lines: List[str]) -> str:
    """Compute content hash of node (normalized for comparison)."""
    src = node_to_source(node, source_lines)
    # Normalize: remove docstrings/comments? No — we want *exact* match.
    # But strip surrounding whitespace, normalize newlines.
    normalized = "\n".join(line.rstrip() for line in src.splitlines()).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def collect_definitions(file_path: Path) -> List[Tuple[str, str, ast.AST]]:
    """
    Returns list of (name, hash, node) for top-level functions/classes/constants.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        try:
            _ = ast.parse(source)
        except:
            print(f"{file_path} ast parse error")
            sys.exit(1)
        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        print(f"[WARN] Syntax error in {file_path}: {e}")
        return []
    definitions = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            name = node.name
            h = hash_node(node, source_lines)
            definitions.append((name, h, node))
        elif isinstance(node, ast.Assign) and is_simple_constant(node):
            name = get_name(node)
            if name:
                h = hash_node(node, source_lines)
                definitions.append((name, h, node))
    return definitions


def ensure_utils_file():
    """Create utils.py if missing, and ensure it has a header comment."""
    if not UTILS_FILE.exists():
        UTILS_FILE.write_text("# Auto-generated utilities from deduplication\n\n")
        return True
    # Check if it's empty or has our marker
    content = UTILS_FILE.read_text()
    if "# Auto-generated" not in content:
        UTILS_FILE.write_text("# Auto-generated utilities from deduplication\n\n" + content)
    return False


def get_imports_from_file(file_path: Path) -> List[str]:
    """Get current import lines (from ... import ..., import ...) from file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return []
    imports = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            imports.append(line.rstrip())
    return imports


def add_import_to_file(file_path: Path, new_import: str):
    """Insert new import at top (after shebang/encoding if present, else top)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith("#!"):
            insert_pos = i + 1
        elif line.startswith("# -*- coding:"):
            insert_pos = i + 1
        elif line.strip().startswith("#") and insert_pos == i:
            # Keep going over comment-only lines
            insert_pos = i + 1
        else:
            break
    if not new_import.endswith("\n"):
        new_import += "\n"
    lines.insert(insert_pos, new_import)
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def remove_definition_from_file(file_path: Path, node: ast.AST, source_lines: List[str]):
    """Remove node from file content (in-place)."""
    start_line = node.lineno - 1
    end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start_line + 1
    # Remove lines
    new_lines = source_lines[:start_line] + source_lines[end_line:]
    # Ensure blank line before/after removal to avoid collapse
    if start_line > 0 and new_lines[start_line - 1].strip() == "":
        pass
    elif start_line > 0:
        new_lines.insert(start_line, "\n")
    if start_line < len(new_lines) and new_lines[start_line].strip() == "":
        pass
    elif start_line < len(new_lines):
        new_lines.insert(start_line + 1, "\n")
    try:
        _ = ast.parse(new_lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines).rstrip() + "\n")
    except:
        print(f"{file_path} ast parse error")


def main():
    # 1. Collect all definitions from all .py files (excluding utils.py)
    py_files = list(CURRENT_DIR.rglob("*.py"))
    py_files = [f for f in py_files if f.name != "utils.py" and f.name != "dedupe.py"]
    hash_to_defs: Dict[str, List[Tuple[Path, str, ast.AST, List[str]]]] = defaultdict(list)
    for fpath in py_files:
        defs = collect_definitions(fpath)
        for name, h, node in defs:
            # Read source_lines fresh
            with open(fpath, "r", encoding="utf-8") as f:
                source_lines = f.read().splitlines()
            hash_to_defs[h].append((fpath, name, node, source_lines))
    duplicates_found = False
    for h, items in hash_to_defs.items():
        if len(items) <= 1:
            continue
        duplicates_found = True
        canonical_file, canonical_name, canonical_node, _ = items[0]
        duplicates = items[1:]
        ensure_utils_file()
        utils_content = UTILS_FILE.read_text()
        print(f"Found duplicate: {canonical_name} ({len(items)} occurrences)")
        for dup_file, name, node, _ in duplicates:
            dup_src = node_to_source(node, dup_file.read_text().splitlines())
            print(f"  → Moving `{name}` from {dup_file} →.py")
            # Add to utils.py
            if not utils_content.endswith("\n\n"):
                utils_content += "\n\n"
            utils_content += dup_src.rstrip() + "\n\n"
            UTILS_FILE.write_text(utils_content)
            # But note: we want to add import to ALL files *except* the canonical one
            # Actually — better: keep one canonical file unchanged, add import to all others (including the one where we removed the def)
            # Let's pick the first item as canonical and leave it alone.
            # For each other item (including original canonical's file? No — only files that *had* the def and lost it)
            # So only modify files where we removed the node (duplicates)
            if dup_file != canonical_file:
                # Add import to dup_file
                add_import_to_file(dup_file, f"from utils import {name}")
                # Remove node from dup_file
                remove_definition_from_file(dup_file, node, dup_file.read_text().splitlines())
            else:
                # Edge case: duplicate was in same file as canonical? AST can't have duplicate names in same file.
                # So this branch shouldn't happen — skip.
                pass
    if not duplicates_found:
        print("No duplicate definitions found.")
    else:
        print("\n✅ Deduplication complete.")
        print("  - Duplicates moved to `utils.py`")
        print("  - Imports added to affected files")
        print("  - Backups saved as `.bak` (if any files modified)")
    for fpath in py_files:
        bak = fpath.with_suffix(fpath.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(fpath, bak)
            print(f"  → Backup: {bak.name}")


if __name__ == "__main__":
    main()
