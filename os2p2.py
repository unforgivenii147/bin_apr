#!/data/data/com.termux/files/usr/bin/python

import ast
import difflib
import os
import re
import sys
from pathlib import Path
from loguru import logger

REPLACEMENTS: dict[tuple[str, str], tuple[str | None, str, str]] = {
    ("os", "path.join"): (
        "pathlib",
        "Path",
        "lambda *args: Path(*args[:-1]).joinpath(args[-1]) if len(args) > 1 else Path(*args)",
    ),
    ("os", "path.exists"): ("pathlib", "Path", "lambda p: Path(p).exists()"),
    ("os", "path.isdir"): ("pathlib", "Path", "lambda p: Path(p).is_dir()"),
    ("os", "path.isfile"): ("pathlib", "Path", "lambda p: Path(p).is_file()"),
    ("os", "path.abspath"): ("pathlib", "Path", "lambda p: Path(p).resolve()"),
    ("os", "path.realpath"): ("pathlib", "Path", "lambda p: Path(p).resolve()"),
    ("os", "path.basename"): ("pathlib", "Path", "lambda p: Path(p).name"),
    ("os", "path.dirname"): ("pathlib", "Path", "lambda p: Path(p).parent"),
    ("os", "path.splitext"): ("pathlib", "Path", "lambda p: (Path(p).stem, Path(p).suffix)"),
    ("os", "path.splitext")[::-1]: None,
    ("os", "path.split"): ("pathlib", "Path", "lambda p: (str(Path(p).parent), Path(p).name)"),
    ("os", "path.getmtime"): ("pathlib", "Path", "lambda p: Path(p).stat().st_mtime"),
    ("os", "path.getsize"): ("pathlib", "Path", "lambda p: Path(p).stat().st_size"),
    ("os", "path.relpath"): (
        "pathlib",
        "Path",
        "lambda p, start='.': Path(p).resolve().relative_to(Path(start).resolve())",
    ),
    ("os", "path.commonpath"): ("pathlib", "Path", "lambda paths: Path(os.path.commonpath(paths))"),
    ("os", "path.samefile"): ("pathlib", "Path", "lambda p1, p2: Path(p1).samefile(Path(p2))"),
    ("os", "path.expanduser"): ("pathlib", "Path", "lambda p: Path(p).expanduser()"),
    ("os", "path.expandvars"): ("pathlib", "Path", "lambda p: Path(p).expandvars()"),
    ("os", "path.normpath"): ("pathlib", "Path", "lambda p: Path(p).resolve()"),
    ("os", "path.normcase"): ("pathlib", "Path", "lambda p: Path(p).resolve().as_posix()"),
    ("os", "makedirs"): ("shutil", "Path", "lambda p, *a, **k: Path(p).mkdir(*a, **k)"),
    ("os", "mkdir"): ("pathlib", "Path", "lambda p: Path(p).mkdir(parents=False, exist_ok=False)"),
    ("os", "rmdir"): ("pathlib", "Path", "lambda p: Path(p).rmdir()"),
    ("os", "remove"): ("pathlib", "Path", "lambda p: Path(p).unlink()"),
    ("os", "rename"): ("pathlib", "Path", "lambda src, dst: Path(src).rename(dst)"),
    ("os", "replace"): ("pathlib", "Path", "lambda src, dst: Path(src).replace(dst)"),
    ("os", "listdir"): ("pathlib", "Path", "lambda p='.': list(Path(p).iterdir())"),
    ("os", "walk"): (
        "pathlib",
        "Path",
        "lambda top: ((str(p), [d.name for d in p.iterdir() if d.is_dir()], [f.name for f in p.iterdir() if f.is_file()]) for p in Path(top).rglob('*') if p.is_dir())",
    ),
    ("os", "stat"): ("pathlib", "Path", "lambda p: Path(p).stat()"),
    ("os", "chdir"): ("pathlib", "Path", "lambda p: os.chdir(p)"),
    ("os", "getcwd"): ("pathlib", None, "lambda: Path.cwd()"),
    ("os", "environ"): ("os", None, "os.environ"),
    ("os", "chmod"): ("pathlib", "Path", "lambda p, mode: Path(p).chmod(mode)"),
    ("os", "chown"): ("pathlib", "Path", "lambda p, uid, gid: Path(p).chown(uid, gid)"),
    ("os", "symlink"): ("pathlib", "Path", "lambda src, dst: Path(dst).symlink_to(src)"),
    ("os", "readlink"): ("pathlib", "Path", "lambda p: str(Path(p).readlink())"),
    ("os", "unlink"): ("pathlib", "Path", "lambda p: Path(p).unlink()"),
    ("os", "rename"): ("pathlib", "Path", "lambda src, dst: Path(src).rename(dst)"),
    ("os", "scandir"): ("pathlib", "Path", "lambda p='.': Path(p).iterdir()"),
}


class OsUsageFinder(ast.NodeVisitor):
    def __init__(self):
        self.uses_os = False
        self.os_import_name: str | None = None
        self.os_path_import_name: str | None = None
        self.os_used_attrs: set[str] = set()
        self.os_path_used_attrs: set[str] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name == "os":
                self.uses_os = True
                self.os_import_name = alias.asname or "os"
            elif alias.name == "os.path":
                self.uses_os = True
                self.os_path_import_name = alias.asname or "os.path"
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "os":
            self.uses_os = True
            for alias in node.names:
                self.os_used_attrs.add(alias.name)
        elif node.module == "os.path":
            self.uses_os = True
            for alias in node.names:
                self.os_path_used_attrs.add(alias.name)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id == self.os_import_name:
            self.uses_os = True
            self.os_used_attrs.add(node.attr)
        if isinstance(node.value, ast.Attribute) and (
            isinstance(node.value.value, ast.Name)
            and node.value.value.id == self.os_import_name
            and (node.value.attr == "path")
        ):
            self.uses_os = True
            self.os_path_used_attrs.add(node.attr)
        self.generic_visit(node)


def rewrite_os_to_pathlib(source: str, tree: ast.AST) -> str:
    source = re.sub("\\bos\\.path\\.join\\s*\\(\\s*([^)]*)\\s*\\)", lambda m: _join_replacer(m.group(1)), source)
    source = re.sub("\\bos\\.getcwd\\s*\\(\\s*\\)", "Path.cwd()", source)
    source = re.sub("\\bos\\.listdir\\s*\\(\\s*\\)", "list(Path().iterdir())", source)
    source = re.sub('\\bos\\.listdir\\s*\\(\\s*"([^"]+)"\\s*\\)', 'list(Path("\\1").iterdir())', source)
    source = re.sub("\\bos\\.listdir\\s*\\(\\s*\\'([^\\']+)\\'\\s*\\)", 'list(Path("\\1").iterdir())', source)
    for attr in [
        "exists",
        "isdir",
        "isfile",
        "abspath",
        "realpath",
        "basename",
        "dirname",
        "splitext",
        "split",
        "getmtime",
        "getsize",
        "relpath",
        "samefile",
        "expanduser",
        "expandvars",
        "normpath",
        "normcase",
    ]:
        pattern = f"\\bos\\.path\\.{attr}\\s*\\(\\s*([^)]*)\\s*\\)"
        repl = _make_pathlib_call(attr)
        source = re.sub(pattern, repl, source)
    for os_attr, (mod, imp, repl) in REPLACEMENTS.items():
        if mod is None and imp == "Path" and ("lambda" in repl):
            continue
        if os_attr[0] == "os" and os_attr[1] != "path":
            pattern = f"\\bos\\.{os_attr[1]}\\s*\\(\\s*([^)]*)\\s*\\)"
            if os_attr[1] in {
                "makedirs",
                "mkdir",
                "rmdir",
                "remove",
                "rename",
                "replace",
                "stat",
                "chmod",
                "chown",
                "symlink",
                "readlink",
                "unlink",
                "scandir",
            }:
                if os_attr[1] == "makedirs":
                    source = re.sub(
                        "\\bos\\.makedirs\\s*\\(\\s*([^,]+)\\s*(?:,\\s*([^)]+))?\\s*\\)",
                        lambda m: (
                            f"Path({m.group(1)}).mkdir(parents=True, exist_ok=True)"
                            if m.group(2) is None
                            else f"Path({m.group(1)}).mkdir({m.group(2)})"
                        ),
                        source,
                    )
                elif os_attr[1] == "mkdir":
                    source = re.sub(
                        "\\bos\\.mkdir\\s*\\(\\s*([^)]+)\\s*\\)",
                        "Path(\\1).mkdir(parents=False, exist_ok=False)",
                        source,
                    )
                elif os_attr[1] == "rmdir":
                    source = re.sub("\\bos\\.rmdir\\s*\\(\\s*([^)]+)\\s*\\)", "Path(\\1).rmdir()", source)
                elif os_attr[1] == "remove":
                    source = re.sub("\\bos\\.remove\\s*\\(\\s*([^)]+)\\s*\\)", "Path(\\1).unlink()", source)
                elif os_attr[1] == "rename":
                    source = re.sub(
                        "\\bos\\.rename\\s*\\(\\s*([^,]+)\\s*,\\s*([^)]+)\\s*\\)", "Path(\\1).rename(\\2)", source
                    )
                elif os_attr[1] == "replace":
                    source = re.sub(
                        "\\bos\\.replace\\s*\\(\\s*([^,]+)\\s*,\\s*([^)]+)\\s*\\)", "Path(\\1).replace(\\2)", source
                    )
                elif os_attr[1] == "stat":
                    source = re.sub("\\bos\\.stat\\s*\\(\\s*([^)]+)\\s*\\)", "Path(\\1).stat()", source)
                elif os_attr[1] == "chmod":
                    source = re.sub(
                        "\\bos\\.chmod\\s*\\(\\s*([^,]+)\\s*,\\s*([^)]+)\\s*\\)", "Path(\\1).chmod(\\2)", source
                    )
                elif os_attr[1] == "chown":
                    source = re.sub(
                        "\\bos\\.chown\\s*\\(\\s*([^,]+)\\s*,\\s*([^,]+)\\s*,\\s*([^)]+)\\s*\\)",
                        "Path(\\1).chown(\\2, \\3)",
                        source,
                    )
                elif os_attr[1] == "symlink":
                    source = re.sub(
                        "\\bos\\.symlink\\s*\\(\\s*([^,]+)\\s*,\\s*([^)]+)\\s*\\)", "Path(\\2).symlink_to(\\1)", source
                    )
                elif os_attr[1] == "readlink":
                    source = re.sub("\\bos\\.readlink\\s*\\(\\s*([^)]+)\\s*\\)", "str(Path(\\1).readlink())", source)
                elif os_attr[1] == "unlink":
                    source = re.sub("\\bos\\.unlink\\s*\\(\\s*([^)]+)\\s*\\)", "Path(\\1).unlink()", source)
                elif os_attr[1] == "scandir":
                    source = re.sub("\\bos\\.scandir\\s*\\(\\s*([^)]*)\\s*\\)", "Path(\\1).iterdir()", source)
    if "Path(" in source and "from pathlib import Path" not in source:
        lines = source.splitlines(keepends=True)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                insert_idx = i + 1
            elif line.strip() and (not line.strip().startswith("#")):
                break
        if insert_idx == 0:
            insert_idx = 1
        lines.insert(insert_idx, "from pathlib import Path\n")
        source = "".join(lines)
    return source


def _join_replacer(args: str) -> str:
    parts = [p.strip() for p in args.split(",") if p.strip()]
    if not parts:
        return "Path()"
    if len(parts) == 1:
        return f"Path({parts[0]})"
    return " / ".join([f"Path({parts[0]})", *parts[1:]])


def _make_pathlib_call(attr: str) -> str:
    mapping = {
        "exists": lambda p: f"Path({p}).exists()",
        "isdir": lambda p: f"Path({p}).is_dir()",
        "isfile": lambda p: f"Path({p}).is_file()",
        "abspath": lambda p: f"Path({p}).resolve()",
        "realpath": lambda p: f"Path({p}).resolve()",
        "basename": lambda p: f"Path({p}).name",
        "dirname": lambda p: f"Path({p}).parent",
        "splitext": lambda p: f"(Path({p}).stem, Path({p}).suffix)",
        "split": lambda p: f"(str(Path({p}).parent), Path({p}).name)",
        "getmtime": lambda p: f"Path({p}).stat().st_mtime",
        "getsize": lambda p: f"Path({p}).stat().st_size",
        "relpath": lambda p: f"Path({p}).resolve().relative_to(Path('.').resolve())",
        "samefile": lambda p: f"Path({p}).exists() and Path({p}).samefile(Path({p}))",
        "expanduser": lambda p: f"Path({p}).expanduser()",
        "expandvars": lambda p: f"Path({p}).expandvars()",
        "normpath": lambda p: f"str(Path({p}).resolve())",
        "normcase": lambda p: f"Path({p}).as_posix().lower()",
    }
    return mapping.get(attr, lambda p: f"Path({p}).{attr}()")


def process_file(path: Path, dry_run: bool = True) -> bool:
    try:
        with path.open("r", encoding="utf-8") as f:
            original = f.read()
    except UnicodeDecodeError:
        print(f"⚠️  Skipping non-UTF-8 file: {path}")
        return False
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        return False
    try:
        tree = ast.parse(original)
    except SyntaxError as e:
        print(f"⚠️  Skipping unparseable file: {path} ({e})")
        return False
    finder = OsUsageFinder()
    finder.visit(tree)
    if not finder.uses_os:
        return False
    new_source = rewrite_os_to_pathlib(original, tree)
    if new_source.strip() == original.strip():
        return False
    if dry_run:
        diff = list(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                new_source.splitlines(keepends=True),
                fromfile=f"{path} (original)",
                tofile=f"{path} (refactored)",
                lineterm="",
            )
        )
        print(f"\n✅ {path} — would change (diff preview):")
        print("".join(diff[:20]))
        if len(diff) > 20:
            print(f"… ({len(diff) - 20} more lines)")
        return True
    try:
        with path.open("w", encoding="utf-8") as f:
            f.write(new_source)
        print(f"✅ {path} — refactored")
        return True
    except Exception as e:
        print(f"❌ Error writing {path}: {e}")
        return False


def collect_files(targets: list[str]) -> list[Path]:
    py_files: list[Path] = []
    excluded_dirs = {
        "__pycache__",
        ".git",
        ".ruff_cache",
        "venv",
        ".venv",
        "env",
        ".env",
        "node_modules",
        ".tox",
        ".mypy_cache",
    }
    for target in targets:
        p = Path(target)
        if not p.exists():
            print(f"⚠️  Path not found: {target}")
            continue
        if p.is_file() and p.suffix == ".py":
            py_files.append(p.resolve())
        elif p.is_dir():
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in excluded_dirs]
                py_files.extend((Path(root) / f for f in files if f.endswith(".py")))
    return sorted(set(py_files))


def main():
    args = sys.argv[1:]
    if not args or {"-h", "--help"} & set(args):
        print(__doc__)
        sys.exit(0)
    dry_run = "--dry" in args
    in_place = "--in-place" in args
    if dry_run and in_place:
        print("❌ Cannot use both --dry and --in-place")
        sys.exit(1)
    if in_place:
        print("⚠️  🔥 IN-PLACE MODE: changes will be written to files.")
        confirm = input("Continue? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            sys.exit(0)
    files_to_process = args
    if not files_to_process:
        files_to_process = ["."]
    files = collect_files(files_to_process)
    if not files:
        print("No Python files found to process.")
        sys.exit(0)
    print(f"🔍 Found {len(files)} Python file(s).")
    changed_count = 0
    for file_path in files:
        if process_file(file_path, dry_run=not in_place):
            changed_count += 1
    print("\n" + "=" * 60)
    if in_place:
        print(f"✅ Refactoring complete: {changed_count} file(s) modified.")
    else:
        print(f"✅ Dry run complete: {changed_count} file(s) would change.")
    print("💡 Always review changes manually before committing!")


if __name__ == "__main__":
    main()
