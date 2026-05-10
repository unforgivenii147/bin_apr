#!/data/data/com.termux/files/usr/bin/python

import sys
from pathlib import Path
from dh import fsz, get_files, gsz, mpf, run_command
from termcolor import cprint


def process_file(fp):
    before = gsz(fp)
    new_path = fp.with_name(fp.stem + ".min" + fp.suffix)
    if not fp.exists():
        return False
    print(f"{fp.name}", end=" ")
    cmd = f"terser --compress --mangle -- {fp}"
    code, output, err = run_command(cmd)
    if code == 0:
        cprint(output, "green")
        new_path.write_text(output)
        fp.unlink()
        after = gsz(new_path)
        diffsize = before - after
        if diffsize == 0:
            cprint("[NO CHANGE]", "white")
        elif diffsize < 0:
            ratio = (before - after) / before * 100
            cprint(f"[OK] + {fsz(diffsize)} {abs(ratio)}%", "yellow")
        elif diffsize > 0:
            ratio = (before - after) / before * 100
            cprint(f"[OK] - {fsz(diffsize)} {ratio}%", "cyan")
        return True
    cprint(f"[ERROR] {err}", "magenta")
    return False


def main():
    args = sys.argv[1:]
    cwd = Path.cwd()
    before = gsz(cwd)
    files = ([Path(p) for p in args] if args else get_files(
        cwd, extensions=[".js", ".ts", ".cjs", ".mjs", ".jsx", ".tsx"]))
    _ = mpf(process_file, files)
    diff_size = before - gsz(cwd)
    cprint(f"space freed : {fsz(diff_size)}", "green")


if __name__ == "__main__":
    sys.exit(main())
