#!/data/data/com.termux/files/usr/bin/python
import sys
from pathlib import Path

from dh import cprint, get_files, mpf3, runcmd, FONT_EXT, unique_path
from fontTools.ttLib import TTFont


def get_font_name(font_path):
    font = TTFont(str(font_path))

    try:
        font = TTFont(file_path)
        for record in font["name"].names:
            if record.nameID == 1:
                return record.string.decode("utf-16-be").strip()
    except:
        pass

    ps_name = font["name"].getName(6, 3, 1, 0, 256)
    if not ps_name:
        family_name = font["name"].getName(1, 3, 1, 0, 256)
        subfamily = font["name"].getName(2, 3, 1, 0, 256)
        if family_name and subfamily:
            return f"{family_name.toUnicode()}-{subfamily.toUnicode()}"
        if family_name:
            return family_name.toUnicode()
    return ps_name.toUnicode()


def process_file(fp):
    new_name = ""
    if fp.suffix not in {".ttf", ".otf"}:
        font_name = get_font_name(fp)
        if not font_name:
            return
        new_name = font_name + fp.suffix
        if new_name != fp.name:
            new_path = fp.with_name(new_name)
            if new_path.exists():
                new_path = unique_path(new_path)
            fp.rename(new_path)
            print(f"{fp.name}->{new_name}")
            return
    cmd = ["tx", fp.name]
    _, txt, _ = runcmd(cmd, show_output=False)
    lines = txt.splitlines()
    for line in lines:
        if "fatal error" in line.lower():
            return False
        if "fontname" in line.lower():
            print(line)
            _, name = line.split(" ", 1)
            name = name.lstrip().rstrip().strip('"')
            if name:
                ext = fp.suffix
                if ext:
                    new_name = f"{name}{ext}"
                else:
                    new_name = name
    if new_name and new_name != fp.name:
        new_path = fp.with_name(new_name)
        if new_path.exists():
            new_path = unique_path(new_path)
        fp.rename(new_path)
        print(f"{fp.name}->", end=" ")
        cprint(f"{new_name}", "cyan")
        return True
    return False


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = []

    if args:
        for arg in args:
            p = Path(arg)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                files.extend(get_files(p, ext=list(FONT_EXT)))
    else:
        files = get_files(cwd, ext=list(FONT_EXT))
    if len(files) == 1:
        process_file(files[0])
        sys.exit(1)
    mpf3(process_file, files)


if __name__ == "__main__":
    sys.exit(main())
