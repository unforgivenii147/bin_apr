#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
from dh import run_command
from loguru import logger

if __name__ == "__main__":
    cwd = Path.cwd()
    for path in cwd.rglob("setup.py"):
        pardir = path.parent
        os.system(f"cd {pardir!s}")
        os.chdir(str(pardir))
        cmd = f"python {path!s} bdist_wheel"
        ret, _, _ = run_command(cmd)
        if ret != 0:
            logger.info("ok")
    for path in cwd.rglob("pyproject.toml"):
        pardir = path.parent
        distdir = pardir / "dist"
        whlfile = list(pardir.rglob("*.whl"))
        if whlfile:
            continue
        os.system(f"cd {pardir!s}")
        os.chdir(str(pardir))
        cmd = "python -m build -w"
        ret, _, _ = run_command(cmd)
        if not ret:
            logger.info("ok")
            continue
    allwhl = list(cwd.rglob("*.whl"))
    logger.info(f"done {len(allwhl)} wheels crwated.")
