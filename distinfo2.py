#!/data/data/com.termux/files/usr/bin/python
import os
import shutil
import sys
from pathlib import Path

from dh import cprint
from loguru import logger

major, minor, _, _, _ = sys.version_info
py_version = f"{major}.{minor}"

ALLOWED = [
    "METADATA",
    "RECORD",
    "WHEEL",
    "top_level.txt",
]
NOT_ALLOWED = [
    "AUTHORS",
    "AUTHORS.md",
    "AUTHORS.rst",
    "AUTHORS.txt",
    "BSD-0-Clause.rst",
    "BSD-2-Clause.rst",
    "CONTRIBUTORS.txt",
    "COPYING",
    "COPYING.GPL",
    "COPYING.LESSER",
    "COPYING.LGPL",
    "COPYING.MPL",
    "COPYING.rst",
    "COPYING.txt",
    "DESCRIPTION.rst",
    "LICENCE",
    "LICENCE.rst",
    "LICENSE",
    "LICENSE-APACHE",
    "LICENSE.APACHE2",
    "LICENSE.markdown-it",
    "LICENSE.md",
    "LICENSE.rst",
    "LICENSE.txt",
    "LICENSE_numpy.txt",
    "LICENSE_scipy.txt",
    "NOTICE",
    "NOTICE.txt",
    "gpl-3-0.txt",
    "pbr.json",
    "toplevel.txt",
]


def process_lic(fp):
    lic_dir = Path(f"{fp}/licenses")
    if lic_dir.exists() and "dist-info" in str(lic_dir.parent):
        shutil.rmtree(lic_dir)
        logger.info(f"{lic_dir} removed.")
    rett = []
    for f in ALLOWED:
        nf = Path(f"{fp}/{f}")
        if not nf.exists() and f not in {"entry_points.txt", "top_level.txt"}:
            rett.append(nf)
    return rett


def main():
    missings = []
    #    cwd = Path(f"/data/data/com.termux/files/usr/lib/python{py_version}/site-packages")
    cwd = Path.cwd()
    for path in cwd.iterdir():
        if path.is_dir() and "dist-info" in path.name:
            if len(os.listdir(path)) < 2:
                cprint(
                    f"{path.name} empty pkg",
                    "cyan",
                )
            missings.extend(process_lic(path))
    for k in missings:
        print(f"{k.parent.name}  ==>", end=" ")
        cprint(f"{k.name}", "yellow")


if __name__ == "__main__":
    sys.exit(main())
