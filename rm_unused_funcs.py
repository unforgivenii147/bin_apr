#!/data/data/com.termux/files/usr/bin/python
import ast
import logging
import multiprocessing
from pathlib import Path
import shutil
from functools import partial

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_defined_and_called(file_path):
    """
    Parses a python file to find defined functions and function calls.
    Note: Static analysis of function calls is complex in Python due to
    dynamic features. This implementation focuses on direct calls.
    """
    try:
        with Path(file_path).open("r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        return None, None, e

    defined = set()
    called = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defined.add(node.name)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called.add(node.func.attr)
    return defined, called, None


def process_file(file_path, dry_run=True):
    """
    Analyzes one file. If not dry_run, removes unused functions.
    This is a simplified approach; removing functions requires
    careful AST manipulation.
    """
    defined, called, err = get_defined_and_called(file_path)
    if err:
        return f"Error parsing {file_path}: {err}"

    unused = [f for f in defined if f not in called and not f.startswith("_")]

    if not unused:
        return None

    if dry_run:
        return f"[DRY-RUN] Would remove {unused} from {file_path}"

    # Backup
    shutil.copy2(file_path, file_path.with_suffix(".py.bak"))

    # Implementation Note: Modifying source code via AST is safer than regex.
    # For brevity, this snippet identifies the file for manual review or
    # advanced node-pruning.
    return f"Processed {file_path}: Found {len(unused)} potentially unused functions."


def run_cleaner(dry_run=True):
    files = list(Path().rglob("*.py"))
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    func = partial(process_file, dry_run=dry_run)

    results = pool.map(func, files)
    for res in results:
        if res:
            print(res)


if __name__ == "__main__":
    # Example usage
    run_cleaner(dry_run=True)
