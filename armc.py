#!/data/data/com.termux/files/usr/bin/python

import re
import ast
import sys
from pathlib import Path
from joblib import Parallel, delayed
from dh import cprint, get_pyfiles

SPECIAL_COMMENT_RE = re.compile("#\\s*(type:|fmt:|pylint|mypy)", re.IGNORECASE)
cwd = Path.cwd().resolve()


def strip_comments(source: str) -> str:
    lines = source.splitlines(keepends=False)
    cleaned_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#!"):
            cleaned_lines.append(line)
            continue
        if stripped.startswith("#") and SPECIAL_COMMENT_RE.search(stripped):
            cleaned_lines.append(line)
            continue
        if stripped.startswith("#"):
            continue
        new_line = ""
        in_single = in_double = False
        j = 0
        while j < len(line):
            char = line[j]
            if char == "'" and (not in_double):
                in_single = not in_single
            elif char == '"' and (not in_single):
                in_double = not in_double
            if not in_single and (not in_double) and (char == "#"):
                comment_text = line[j:]
                if SPECIAL_COMMENT_RE.search(comment_text):
                    new_line += comment_text
                break
            new_line += char
            j += 1
        cleaned_lines.append(new_line.rstrip())
    return "\n".join(cleaned_lines).rstrip() + "\n"


def process_file(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
        cleaned = strip_comments(original)
        if cleaned.strip() == original.strip():
            return
        try:
            ast.parse(cleaned)
        except SyntaxError:
            cprint(
                f"⚠️ Skipped (syntax error after clean): {path.relative_to(cwd)}"
            )
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)
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
        (delayed(process_file)(f) for f in python_files))


if __name__ == "__main__":
    main()
