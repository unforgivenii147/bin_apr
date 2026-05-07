#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
import sys
from pathlib import Path

from dh import MIME2EXT, cprint, unique_path


def fix_by_shebang(fp) -> bool:
    content = fp.read_text(encoding="utf8")
    fl = content.splitlines()[0]
    if fl.startswith("#!") and ("bash" in fl or "/bin/sh" in fl):
        new_path = fp.with_suffix(".sh")
        if new_path.exists():
            new_path = unique_path(new_path)
        fp.rename(new_path)
        return True
    elif fl.startswith("#!") and "python" in fl:
        new_path = fp.with_suffix(".py")
        if new_path.exists():
            new_path = unique_path(new_path)
        fp.rename(new_path)
        return True
    elif fl.startswith("#!") and "perl" in fl:
        new_path = fp.with_suffix(".pl")
        if new_path.exists():
            new_path = unique_path(new_path)
        print(f"rename {fp.name} -> {new_path.name}")
        ans = input("?")
        if ans == "y":
            fp.rename(new_path)
            return True
        return False
    elif fl.startswith("#!") and "node" in fl:
        new_path = fp.with_suffix(".js")
        if new_path.exists():
            new_path = unique_path(new_path)
        print(f"rename {fp.name} -> {new_path.name}")
        ans = input("?")
        if ans == "y":
            fp.rename(new_path)
            return True
        return False
    else:
        return False
    return False


def get_file_mime(file_path):
    try:
        result = subprocess.run(
            [
                "file",
                "--brief",
                "--mime-type",
                file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(
            f"Error detecting file type for {file_path}: {e}",
            file=sys.stderr,
        )
        return None


def safe_rename(old_path, new_path):
    base, ext = os.path.splitext(new_path)
    counter = 1
    while Path(new_path).exists():
        new_path = f"{base}_{counter}{ext}"
        counter += 1
    cprint(f"{old_path} -> {new_path} ?")
    Path(old_path).rename(new_path)
    return new_path


def check_files(directory):
    mismatched_files = []
    for root, _, files in os.walk(directory):
        for name in files:
            file_path = Path(root) / name
            if ".git" in file_path.parts or "__pycache__" in file_path.parts:
                continue
            ext = file_path.suffix.lower()
            if fix_by_shebang(file_path):
                continue
            if ext in {
                ".eot",
                ".svg",
                ".woff2",
                ".woff",
                ".ttf",
                ".c",
                ".md",
                ".py",
                ".pdf",
                ".html",
                ".js",
                ".css",
            }:
                continue
            mime = get_file_mime(file_path)
            print(f"{name} --> {mime}")
            if mime:
                expected_exts = MIME2EXT.get(mime, [])
                if expected_exts and ext not in expected_exts:
                    new_path = None
                    new_ext = expected_exts[0]
                    new_name = os.path.splitext(name)[0] + new_ext
                    new_path = Path(root) / new_name
                    if new_name == name:
                        continue
                    if new_path.exists():
                        new_path = unique_path(new_path)
                    file_path.rename(new_path)
                    #                    new_path = safe_rename(file_path, new_path)
                    mismatched_files.append(
                        (
                            file_path,
                            ext,
                            mime,
                            new_path,
                        )
                    )
    return mismatched_files


def main():
    cwd = Path.cwd()
    mismatches = check_files(cwd)
    if mismatches:
        print("Files with mismatched extensions:")
        for (
            file_path,
            _ext,
            mime,
            new_path,
        ) in mismatches:
            if new_path:
                print(f"\033[5;93m{file_path.name} {mime} \033[5;96m{new_path.name}]\033[0m")
            else:
                print(f"{file_path.name} -> \033[5m;94mdetected: {mime}\033[0m")
    else:
        cprint("no mismatch")


if __name__ == "__main__":
    main()
