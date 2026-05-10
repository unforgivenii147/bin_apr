#!/data/data/com.termux/files/usr/bin/python

import ast
from pathlib import Path
from joblib import Parallel, delayed
from dh import cprint, get_pyfiles

cwd = Path.cwd()


class DocstringRemover(ast.NodeTransformer):

    def _remove_docstring(self, node):
        if (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant) and
                isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        return node

    def visit_Module(self, node):
        self.generic_visit(node)
        return self._remove_docstring(node)

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        return self._remove_docstring(node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        return self._remove_docstring(node)

    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)
        return self._remove_docstring(node)


def process_file(path: Path):
    try:
        original = path.read_text(encoding="utf-8")
        tree = ast.parse(original)
        transformer = DocstringRemover()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        cleaned = ast.unparse(new_tree)
        try:
            ast.parse(cleaned)
        except SyntaxError:
            cprint(f"syntax error: {path.relative_to(cwd)}")
            return
        if cleaned.strip() == original.strip():
            return
        path.write_text(cleaned + "\n", encoding="utf-8")
        print(f"✅ Cleaned: {path.relative_to(cwd)}")
    except Exception as e:
        print(f"❌ Error processing {path}: {e}")


def main():
    python_files = get_pyfiles(cwd)
    if not python_files:
        print("No Python files found.")
        return
    print(f"Discovered {len(python_files)} python-like files...")
    Parallel(n_jobs=-1, prefer="processes")(
        (delayed(process_file)(p) for p in python_files))


if __name__ == "__main__":
    main()
