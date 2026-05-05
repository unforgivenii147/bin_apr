#!/data/data/com.termux/files/usr/bin/python
"""
Find Python files that contain non-top-level import statements.

- Traverses current directory recursively using pathlib.
- For each *.py file, parses AST and finds import statements that
  are NOT at module top level (e.g., inside functions, classes, etc.).
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


class ImportVisitor(ast.NodeVisitor):
    """
    Visitor that records import statements that are not at module top level.

    Top-level = direct children of the Module body.
    Anything nested (function, class, if, loop, etc.) is considered non-top-level.
    """

    def __init__(self) -> None:
        self._nesting_level = 0
        self.non_top_level_imports: list[ast.stmt] = []

    def _is_top_level(self) -> bool:
        # Module body is visited with _nesting_level == 0.
        # All nested scopes/blocks increment nesting_level.
        return self._nesting_level == 0

    # Generic nesting helpers
    def _visit_nested(self, node: ast.AST):
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    # Nodes that introduce nesting
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_nested(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_nested(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self._visit_nested(node)

    def visit_For(self, node: ast.For):
        self._visit_nested(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self._visit_nested(node)

    def visit_While(self, node: ast.While):
        self._visit_nested(node)

    def visit_If(self, node: ast.If):
        self._visit_nested(node)

    def visit_With(self, node: ast.With):
        self._visit_nested(node)

    def visit_AsyncWith(self, node: ast.AsyncWith):
        self._visit_nested(node)

    def visit_Try(self, node: ast.Try):
        self._visit_nested(node)

    # Import handlers
    def visit_Import(self, node: ast.Import):
        if not self._is_top_level():
            self.non_top_level_imports.append(node)
        # Still visit children (aliases), but they don't affect nesting
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if not self._is_top_level():
            self.non_top_level_imports.append(node)
        self.generic_visit(node)


def find_python_files(root: Path) -> Iterable[Path]:
    """Yield all .py files under root (recursively)."""
    return root.rglob("*.py")


def format_import(node: ast.stmt) -> str:
    """Return a human-readable string representation of an import statement node."""
    if isinstance(node, ast.Import):
        # import x, y as z
        parts = []
        for alias in node.names:
            if alias.asname:
                parts.append(f"{alias.name} as {alias.asname}")
            else:
                parts.append(alias.name)
        return "import " + ", ".join(parts)

    if isinstance(node, ast.ImportFrom):
        # from x import y as z
        module = node.module or ""
        parts = []
        for alias in node.names:
            if alias.asname:
                parts.append(f"{alias.name} as {alias.asname}")
            else:
                parts.append(alias.name)
        level_dots = "." * (node.level or 0)
        module_str = level_dots + module if module else level_dots
        return f"from {module_str} import " + ", ".join(parts)

    return "<unknown import>"


def inspect_file(path: Path):
    """Inspect a single .py file, returning list of (lineno, import_str)."""
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback encoding if needed
        source = path.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        print(f"[WARN] Skipping {path} (syntax error: {e})")
        return []

    visitor = ImportVisitor()
    visitor.visit(tree)

    results = []
    for node in visitor.non_top_level_imports:
        lineno = getattr(node, "lineno", "?")
        results.append((lineno, format_import(node)))
    return results


def main():
    root = Path.cwd()
    any_found = False

    for py_file in find_python_files(root):
        imports = inspect_file(py_file)
        if not imports:
            continue

        any_found = True
        print(f"\n{py_file}:")
        for lineno, stmt in imports:
            print(f"  line {lineno}: {stmt}")

    if not any_found:
        print("No non-top-level imports found.")


if __name__ == "__main__":
    main()
