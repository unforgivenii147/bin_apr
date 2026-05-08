#!/data/data/com.termux/files/usr/bin/python
import os
import subprocess
from pathlib import Path


def is_git_repo(path: Path) -> bool:
    """Return True if the path contains a .git directory."""
    return (path / ".git").is_dir()


def git_pull(repo_path: Path):
    print(f"\n==> Pulling in repo: {repo_path}")
    try:
        subprocess.run(["git", "-C", str(repo_path), "restore", "."], check=True)
    except subprocess.CalledProcessError:
        print(f"⚠️  git pull failed in: {repo_path}")


def main():
    root = Path.cwd()
    for dirpath, _dirnames, _filenames in os.walk(root):
        current = Path(dirpath)
        # If `.git` folder exists here → repo root found
        if is_git_repo(current):
            git_pull(current)
            # Avoid descending into this repo's subdirectories again
            # (prevents duplicate pulls, speeds up traversal)
    #            dirnames[:] = [ d for d in dirnames if d not in {".git"}]
    print("\nDone.")


if __name__ == "__main__":
    main()
