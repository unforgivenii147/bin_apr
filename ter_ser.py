#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path

from dh import fsz, get_files, gsz, mpf3, runcmd, cprint
import tempfile


def safe_run(path):
    content = path.read_text(encoding="utf-8")
    temp_filename = ""
    with tempfile.NamedTemporaryFile(
        mode="w+",
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    ) as temp_f:
        temp_filename = temp_f.name
        temp_f.write(content)
        temp_f.flush()
    cmd = ["terser", "--compress", "--mangle", "--", f"{str(temp_filename)}"]
    res, txt, err = runcmd(cmd, show_output=False)
    temp_path = Path(temp_filename)
    temp_path.write_text(txt, encoding="utf8")
    if res != 0:
        print(
            f"Error running terser: {err}",
            file=sys.stderr,
        )
        temp_path.unlink()
        return False
    temp_path.rename(path)
    return True


def process_file(fp):
    before = gsz(fp)
    if not fp.exists():
        return False
    print(f"{fp.name}", end=" ")
    res = safe_run(fp)
    if res:
        after = gsz(fp)
        diffsize = before - after
        if not diffsize:
            cprint("[NO CHANGE]", "white")
        if diffsize:
            ratio = (diffsize / before) * 100
            cprint(f"[OK] + {fsz(diffsize)} {abs(ratio):.1f}%", "cyan")
        return True
    cprint(f"[ERROR]", "red")
    return False


def main():
    args = sys.argv[1:]
    cwd = Path.cwd()
    before = gsz(cwd)
    files = (
        [Path(p) for p in args] if args else get_files(cwd, extensions=[".js", ".ts", ".cjs", ".mjs", ".jsx", ".tsx"])
    )
    _ = mpf3(process_file, files)
    diff_size = before - gsz(cwd)
    cprint(f"space freed : {fsz(diff_size)}", "green")


if __name__ == "__main__":
    sys.exit(main())
