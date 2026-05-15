#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path

from dh import fsz, get_files, gsz, mpf3, runcmd, cprint


def safe_run(path):
    cmd = ["terser", "--compress", "--mangle", "--", str(path)]
    res, txt, err = runcmd(cmd, show_output=False)
    if res != 0:
        print(
            f"Error running terser: {err}",
            file=sys.stderr,
        )
        return False
    path.write_text(txt, encoding="utf8")
    return True


def process_file(fp):
    if "site-packages" in fp.parts
    before = gsz(fp)
    if not fp.exists() or not before:
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
