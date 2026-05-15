#!/data/data/com.termux/files/usr/bin/python


from utils import (
    cwd,
    process_file,
)
#!/data/data/com.termux/files/usr/bin/python

from pathlib import Path

from dh import get_files


def process_file(fp: Path):
    if not fp.exists():
        return False
    print(f"processing  ... {fp.name}")
    last_tag_pos = -1
    tags = ("</svg>", "</html>", "</body>", "</script>", "</div>")
    content = []
    with fp.open("r", encoding="utf-8") as f:
        for line in f:
            content.append(line)
    for i, line in reversed(list(enumerate(content))):
        for tag in tags:
            idx = line.rfind(tag)
            if idx != -1:
                last_tag_pos = sum((len(content[j]) for j in range(i))) + idx + len(tag)
                break
        if last_tag_pos != -1:
            break
    if last_tag_pos == -1:
        return True
    trimmed = "".join(content)[:last_tag_pos]
    fp.write_text(trimmed, encoding="utf-8")
    return True


if __name__ == "__main__":
    cwd = Path().cwd()
    for path in get_files(cwd):
        if path.suffix in {".html", ".htm", ".svg", ".xml"}:
            process_file(path)
