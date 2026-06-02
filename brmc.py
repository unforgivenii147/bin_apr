#!/data/data/com.termux/files/usr/bin/python
import ast
import sys
from pathlib import Path

from dh import DOC_TH1, cprint, fsz, get_pyfiles, gsz, mpf3, read_lines

DOCTH1 = DOC_TH1 * 2
cwd = Path.cwd()


def preprocess_code(code):
    nl = []
    removed = 0
    lines = code.splitlines()
    for line in lines:
        stripped = line.lstrip().rstrip().strip()
        if stripped.startswith(DOC_TH1) and stripped.endswith(DOC_TH1) and (stripped != DOCTH1):
            print(line)
            removed += 1
            continue
        nl.append(line)
    if removed:
        try:
            new_code = "\n".join(nl)
            _ = ast.parse(code)
            return new_code
        except:
            cprint("ast parse error")
            return code
    else:
        return code


class DocstringRemover(ast.NodeTransformer):
    def _remove_docstring(self, node):
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            if len(node.body) == 1:
                node.body = [ast.Pass()]
            else:
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


class DocstringRemover(ast.NodeTransformer):
    def _remove_docstring(self, node):
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            node.body = node.body[1:]
        return node


def process_file(path: Path):
    before = gsz(path)
    try:
        code = path.read_text(encoding="utf-8")
        first_line = ""
        if code.startswith("#!"):
            lines = code.splitlines(keepends=True)
            first_line = lines[0]
            code = "".join(lines[1:])
        pre_code = preprocess_code(code)
        tree = ast.parse(pre_code)
        transformer = DocstringRemover()
        new_tree = transformer.visit(tree)
        new_tree = ast.fix_missing_locations(new_tree)
        newcode = ast.unparse(new_tree)
        if first_line:
            newcode = first_line + newcode
        try:
            ast.parse(newcode)
        except SyntaxError:
            cprint(f"ast parse error: {path.name}")
            return
        if len(newcode.strip()) == len(code.strip()):
            print(f"{path.name} (no change)")
            return
        path.write_text(newcode, encoding="utf-8")
        after = gsz(path)
        dsz = before - after
        if dsz:
            ratio = dsz / before * 100
            print(f"✅ {path.name}", end=" | ")
            cprint(f"{fsz(dsz)} | {ratio:.1f}%", "cyan")
            return
        else:
            cprint(f"{path.name} (no change)", "grey")
            return
    except Exception as e:
        cprint(f"❌ {path.name}: {e}", "yellow")


def main():
    args = sys.argv[1:]
    files = [Path(p) for p in args] if args else get_pyfiles(cwd)
    if not files:
        print("No Python files found.")
        return
    if len(files) == 1:
        process_file(files[0])
        sys.exit(1)
    mpf3(process_file, files)


if __name__ == "__main__":
    main()
