#!/data/data/com.termux/files/usr/bin/python
"""
cleancss -o one-min.css one.css
  %> cleancss -o merged-and-minified.css one.css two.css three.css
  %> cleancss one.css two.css three.css | gzip -9 -c > merged-minified-and-gzipped.css.gz

Formatting options:
  %> cleancss --format beautify one.css
  %> cleancss --format keep-breaks one.css
  %> cleancss --format 'indentBy:1;indentWith:tab' one.css
  %> cleancss --format 'breaks:afterBlockBegins=on;spaces:aroundSelectorRelation=on' one.css
  %> cleancss --format 'breaks:afterBlockBegins=2;spaces:aroundSelectorRelation=on' one.css

Level 0 optimizations:
  %> cleancss -O0 one.css

Level 1 optimizations:
  %> cleancss -O1 one.css
  %> cleancss -O1 removeQuotes:off;roundingPrecision:4;specialComments:1 one.css
  %> cleancss -O1 all:off;specialComments:1 one.css

Level 2 optimizations:
  %> cleancss -O2 one.css
  %> cleancss -O2 mergeMedia:off;restructureRules:off;mergeSemantically:on;mergeIntoShorthands:off one.css
  %> cleancss -O2 all:off;removeDuplicateRules:on one.css
"""

import sys
from pathlib import Path

from dh import fsz, get_files, gsz, mpf3, runcmd, cprint


def process_file(path):
    before = gsz(path)
    if not path.exists():
        return False
    print(f"{path.name}", end=" ")
    cmd = ["cleancss", "--format", "beautify", str(path), "-o", str(path)]
    res, _, err = runcmd(cmd, show_output=True)

    if not res:
        after = gsz(path)
        diffsize = before - after
        if not diffsize:
            cprint("[NO CHANGE]", "white")
        if diffsize:
            ratio = (diffsize / before) * 100
            cprint(f"[OK] - {fsz(diffsize)} {abs(ratio):.1f}%", "cyan")
        return True
    cprint(f"[ERROR]", "red")
    return False


def main():
    args = sys.argv[1:]
    cwd = Path.cwd()
    before = gsz(cwd)
    files = [Path(p) for p in args] if args else get_files(cwd, extensions=[".css", ".min.css"])
    _ = mpf3(process_file, files)
    diff_size = before - gsz(cwd)
    cprint(f"space freed : {fsz(diff_size)}", "green")


if __name__ == "__main__":
    sys.exit(main())
