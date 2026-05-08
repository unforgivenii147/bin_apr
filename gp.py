#!/data/data/com.termux/files/usr/bin/python
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from loguru import logger


def run(cmd) -> None:
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        logger.info(
            f"Command failed: {cmd}",
            file=sys.stderr,
        )
        sys.exit(1)


def ensure_git_repo() -> None:
    try:
        subprocess.check_output(
            "git rev-parse --is-inside-work-tree",
            shell=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError:
        logger.info(
            "Not inside a Git repository.",
            file=sys.stderr,
        )
        sys.exit(1)


def symlink_global_gitignore() -> None:
    home_gitignore = Path.home() / ".gitignore"
    local_gitignore = Path(".gitignore")
    if not home_gitignore.exists():
        logger.info("~/.gitignore does not exist. Create it first if needed.")
        return
    if local_gitignore.exists():
        return
    try:
        local_gitignore.symlink_to(home_gitignore)
        logger.info(f"Symlinked {home_gitignore} → {local_gitignore}")
    except Exception as e:
        logger.info(
            f"Failed to create symlink: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def get_current_branch():
    cmd = "git rev-parse --abbrev-ref HEAD"
    return subprocess.check_output(cmd, shell=True).decode().strip()


def main() -> None:
    ensure_git_repo()
    symlink_global_gitignore()
    run("git add -A")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-commit at {now}"
    subprocess.call(
        f"git commit -m '{commit_msg}'",
        shell=True,
    )
    branch = get_current_branch()
    run(f"git push origin {branch}")
    logger.info(f"Pushed to origin/{branch} with message: {commit_msg}")


if __name__ == "__main__":
    main()
