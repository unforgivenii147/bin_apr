#!/data/data/com.termux/files/usr/bin/python
import shutil
import subprocess
import sys

from loguru import logger


def run_git_command(cmd, check=True, capture_output=True):
    try:
        return subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logger.info(f"Error running command: {cmd}")
        logger.info(f"Error: {e}")
        if e.stderr:
            logger.info(f"Stderr: {e.stderr}")
        return None


def is_git_repository():
    return run_git_command("git rev-parse --git-dir", check=False) is not None


def get_current_branch():
    result = run_git_command("git branch --show-current")
    if result and result.stdout:
        return result.stdout.strip()
    return None


def get_main_branch_name():
    result = run_git_command("git remote show origin", check=False)
    if result and "HEAD branch" in result.stdout:
        for line in result.stdout.split("\n"):
            if "HEAD branch" in line:
                return line.split(":")[1].strip()
    result = run_git_command("git branch -l")
    if result:
        branches = [b.strip().replace("* ", "") for b in result.stdout.split("\n") if b.strip()]
        for branch in branches:
            if branch in {"main", "master"}:
                return branch
    return "main"


def get_all_branches():
    result = run_git_command("git branch -l")
    if not result:
        return []
    branches = []
    for line in result.stdout.split("\n"):
        if line.strip():
            branch = line.strip().replace("* ", "")
            branches.append(branch)
    return branches


def delete_branches_except_main():
    main_branch = get_main_branch_name()
    branches = get_all_branches()
    logger.info(f"Main branch: {main_branch}")
    logger.info(f"Found branches: {', '.join(branches)}")
    deleted_branches = []
    for branch in branches:
        if branch != main_branch:
            logger.info(f"Deleting branch: {branch}")
            result = run_git_command(
                f"git branch -D {branch}",
                check=False,
            )
            if result and result.returncode == 0:
                deleted_branches.append(branch)
                logger.info(f"✓ Deleted branch: {branch}")
            else:
                logger.info(f"✗ Failed to delete branch: {branch}")
    return deleted_branches


def reset_to_last_commit() -> bool:
    logger.info("Resetting to last commit...")
    result = run_git_command("git rev-parse HEAD")
    if not result:
        return False
    current_commit = result.stdout.strip()
    logger.info(f"Current commit: {current_commit}")
    main_branch = get_main_branch_name()
    commands = [
        "git checkout --orphan temp_branch",
        "git add -A",
        'git commit -m "Squashed history - only keeping last commit"',
        f"git branch -D {main_branch}",
        f"git branch -m {main_branch}",
    ]
    for cmd in commands:
        logger.info(f"Running: {cmd}")
        result = run_git_command(cmd, check=False)
        if not result or result.returncode != 0:
            logger.info(f"Failed to run: {cmd}")
            return False
    logger.info("✓ Successfully reset to last commit")
    return True


def alternative_reset_method() -> None:
    logger.info("Using alternative reset method...")
    commands = [
        "git branch backup-before-cleanup",
        "git reset --hard HEAD",
        "git reflog expire --expire=now --all",
        "git gc --prune=now --aggressive",
    ]
    for cmd in commands:
        logger.info(f"Running: {cmd}")
        result = run_git_command(cmd, check=False)
        if not result or result.returncode != 0:
            logger.info(f"Warning: Command failed: {cmd}")
    logger.info("✓ Alternative reset completed")


def create_backup() -> bool | None:
    backup_dir = f"git_backup_{subprocess.getoutput('date +%Y%m%d_%H%M%S')}"
    logger.info(f"Creating backup in: {backup_dir}")
    try:
        shutil.copytree(
            ".",
            backup_dir,
            ignore=shutil.ignore_patterns(".git"),
        )
        logger.info(f"✓ Backup created: {backup_dir}")
        return True
    except Exception as e:
        logger.info(f"✗ Failed to create backup: {e}")
        return False


def main() -> None:
    logger.info("=" * 60)
    logger.info("GIT REPOSITORY CLEANER")
    logger.info("WARNING: This is a DESTRUCTIVE operation!")
    logger.info("It will delete all commits except the last one")
    logger.info("and delete all branches except main/master.")
    logger.info("=" * 60)
    if not is_git_repository():
        logger.info("Error: Not a git repository!")
        sys.exit(1)
    response = input("\nAre you sure you want to continue? (yes/NO): ")
    if response.lower() not in {"yes", "y"}:
        logger.info("Operation cancelled.")
        sys.exit(0)
    logger.info("\n1. Creating backup...")
    if not create_backup():
        response = input("Backup failed. Continue anyway? (yes/NO): ")
        if response.lower() not in {"yes", "y"}:
            logger.info("Operation cancelled.")
            sys.exit(0)
    logger.info("\n2. Checking repository status...")
    main_branch = get_main_branch_name()
    current_branch = get_current_branch()
    branches = get_all_branches()
    logger.info(f"   Current branch: {current_branch}")
    logger.info(f"   Main branch: {main_branch}")
    logger.info(f"   All branches: {', '.join(branches)}")
    if current_branch != main_branch:
        logger.info(f"\n3. Switching to main branch: {main_branch}")
        result = run_git_command(
            f"git checkout {main_branch}",
            check=False,
        )
        if not result or result.returncode != 0:
            logger.info(f"Failed to switch to {main_branch}")
            sys.exit(1)
    logger.info(f"\n4. Deleting branches except {main_branch}...")
    deleted_branches = delete_branches_except_main()
    if deleted_branches:
        logger.info(f"   Deleted {len(deleted_branches)} branches")
    else:
        logger.info("   No branches to delete")
    logger.info("\n5. Resetting ...")
    if not alternative_reset_method():
        reset_to_last_commit()
    logger.info("\n6. Final status:")
    result = run_git_command("git log --oneline")
    if result:
        logger.info("   Commit history:")
        for line in result.stdout.strip().split("\n"):
            logger.info(f"     {line}")
    branches = get_all_branches()
    logger.info(f"   Remaining branches: {', '.join(branches)}")
    logger.info("\n✓ Cleanup completed!")
    logger.info("⚠️  Remember: You may need to force push to remote:")
    logger.info(f"   git push --force origin {main_branch}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.info(f"\nAn error : {e}")
        sys.exit(1)
