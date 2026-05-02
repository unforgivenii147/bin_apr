#!/data/data/com.termux/files/usr/bin/python
import re
import sys
from pathlib import Path
from dhh import fsz, get_files, gsz, mpf3

blank_line = "\n"
IMAGE_RE = re.compile(r"^\s*(\.\.\s+image::|:target:|:alt:)", re.IGNORECASE)


def process_file(path: Path):
    print(f"Processing {path.name}")
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"⚠️  Skipping {path}: {e}")
        return
    lines = content.splitlines(keepends=True)  # keep original line endings
    modified_lines = []
    replaced_count = 0
    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped.lower().startswith("classifier"):
            modified_lines.append("\n")
            replaced_count += 1
            continue
        if stripped.startswith("[![") or stripped.lower().startswith("project-url"):
            modified_lines.append("\n")
            replaced_count += 1
            continue
        if stripped.startswith(
            (
                "Metadata-Version",
                "Home-page",
                "Author",
                "Maintainer",
                "License",
                "Platform",
                "Requires-Python",
                "Description-Content-Type",
                "Provides-Extra",
            )
        ):
            modified_lines.append("\n")
            replaced_count += 1
            continue
        if IMAGE_RE.match(stripped):
            modified_lines.append("\n")
            replaced_count += 1
            continue
        modified_lines.append(line)
    if not replaced_count:
        return
    new_content = "".join(modified_lines)
    try:
        path.write_text(new_content, encoding="utf-8")
        print(f"✅ Replaced {replaced_count} line(s) in {path.name}")
    except Exception as e:
        print(f"❌ Failed to write {path}: {e}")


def main():
    cwd = Path.cwd()
    before = gsz(cwd)
    args = sys.argv[1:]
    files = (
        [Path(f) for f in args]
        if args
        else get_files(
            cwd,
            recursive=True,
            extensions=[".metadata", ".md"],
        )
    )
    metafiles = list(cwd.rglob("METADATA"))
    if metafiles:
        files.extend(metafiles)
    print(f"{len(files)} files found.")
    for f in files:
        process_file(f)
    diff_size = before - gsz(cwd)
    print(f"space saved : {fsz(diff_size)}")


if __name__ == "__main__":
    main()
