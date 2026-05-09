#!/data/data/com.termux/files/usr/bin/python
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from loguru import logger


def run(cmd) -> bool | None:
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def in_git_repo():
    return run("git rev-parse --is-inside-work-tree > /dev/null 2>&1")


def ensure_gitignore() -> None:
    repo_gitignore = Path(".gitignore")
    global_gitignore = Path.home() / ".gitignore_global"
    if repo_gitignore.exists():
        logger.info(".gitignore already exists.")
        return
    if global_gitignore.exists():
        logger.info("Copying global .gitignore_global to local .gitignore...")
        shutil.copy(global_gitignore, repo_gitignore)
    else:
        logger.info("No local .gitignore and no ~/.gitignore_global found. Skipping.")


def find_python_scripts_without_extension():
    py_files = []
    for root, _, files in os.walk("."):
        for f in files:
            if "." in f:
                continue
            path = os.path.join(root, f)
            try:
                with Path(path).open(encoding="utf-8", errors="ignore") as file:
                    first_line = file.readline().strip()
                    if first_line.startswith("#!") and "python" in first_line.lower():
                        py_files.append(path)
            except (OSError, UnicodeDecodeError):
                continue
    return py_files


def main() -> None:
    if not in_git_repo():
        logger.info("Not inside a Git repository. Doing nothing.")
        return
    ensure_gitignore()
    python_files = []
    for root, _, files in os.walk("."):
        python_files.extend(os.path.join(root, f) for f in files if f.endswith(".py"))
    python_files.extend(find_python_scripts_without_extension())
    if not python_files:
        logger.info("No Python files found.")
        return
    logger.info("Formatting Python files with black:")
    for f in python_files:
        logger.info("  ->", f)
        if not run(f"black {f}"):
            logger.info(f"Black failed for {f}.")
            return
    logger.info("Running git add .")
    if not run("git add ."):
        logger.info("git add failed.")
        return
    commit_message = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Committing with message: {commit_message}")
    commit_success = run(f'git commit -m "{commit_message}"')
    if not commit_success:
        logger.info("Nothing to commit or commit failed.")
        return
    logger.info("Pushing changes...")
    if not run("git push"):
        logger.info("git push failed.")
        return
    logger.info("Done!")


if __name__ == "__main__":
    main()
