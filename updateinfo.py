#!/data/data/com.termux/files/usr/bin/python
import re
import sys
from pathlib import Path
from loguru import logger

NEW_INFO = {
    "name": "Isaac Onagh",
    "email": "mkalafsaz@gmail.com",
    "github_username": "unforgivenii147",
}


def update_setup_py(file_path: Path) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        content = re.sub(
            r'author\s*=\s*["\'][^"\']*["\']',
            f'author="{NEW_INFO["name"]}"',
            content,
        )
        content = re.sub(
            r'author_email\s*=\s*["\'][^"\']*["\']',
            f'author_email="{NEW_INFO["email"]}"',
            content,
        )
        content = re.sub(
            r'(https?://github\.com/)[^/]+(/[^"\']*)',
            rf"\g<1>{NEW_INFO['github_username']}\g<2>",
            content,
        )
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"✅ Updated {file_path}")
            return True
        logger.info(f"No changes needed in {file_path}")
        return False
    except Exception as e:
        logger.info(f"❌ Error updating {file_path}: {e}")
        return False


def update_pyproject_toml(file_path: Path) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        if "[project]" in content:
            author_pattern = (
                r'(authors\s*=\s*\[\s*\{[^}]*name\s*=\s*["\'][^"\']*["\'][^}]*email\s*=\s*["\'][^"\']*["\'][^}]*\})'
            )

            def replace_author(match):
                author_block = match.group(1)
                author_block = re.sub(
                    r'name\s*=\s*["\'][^"\']*["\']',
                    f'name = "{NEW_INFO["name"]}"',
                    author_block,
                )
                return re.sub(
                    r'email\s*=\s*["\'][^"\']*["\']',
                    f'email = "{NEW_INFO["email"]}"',
                    author_block,
                )

            content = re.sub(
                author_pattern,
                replace_author,
                content,
                flags=re.DOTALL,
            )
        content = re.sub(
            r"(https?://github\.com/)[^/]+(/)",
            rf"\g<1>{NEW_INFO['github_username']}\g<2>",
            content,
        )
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"✅ Updated {file_path}")
            return True
        logger.info(f"ℹ️  No changes needed in {file_path}")
        return False
    except Exception as e:
        logger.info(f"❌ Error updating {file_path}: {e}")
        return False


def update_setup_cfg(file_path: Path) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        if "[metadata]" in content:
            content = re.sub(
                r"^author\s*=\s*.*$",
                f"author = {NEW_INFO['name']}",
                content,
                flags=re.MULTILINE,
            )
            content = re.sub(
                r"^author_email\s*=\s*.*$",
                f"author_email = {NEW_INFO['email']}",
                content,
                flags=re.MULTILINE,
            )
        content = re.sub(
            r"(https?://github\.com/)[^/]+(/)",
            rf"\g<1>{NEW_INFO['github_username']}\g<2>",
            content,
        )
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"✅ Updated {file_path}")
            return True
        logger.info(f"ℹ️  No changes needed in {file_path}")
        return False
    except Exception as e:
        logger.info(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    logger.info("🔍 Scanning for configuration files...")
    logger.info("📝 New information:")
    logger.info(f"   Name: {NEW_INFO['name']}")
    logger.info(f"   Email: {NEW_INFO['email']}")
    logger.info(f"   GitHub Username: {NEW_INFO['github_username']}")
    logger.info("-" * 50)
    files_to_update = [
        (Path("setup.py"), update_setup_py),
        (
            Path("pyproject.toml"),
            update_pyproject_toml,
        ),
        (Path("setup.cfg"), update_setup_cfg),
    ]
    updated_count = 0
    for file_path, update_func in files_to_update:
        if file_path.exists():
            if update_func(file_path):
                updated_count += 1
        else:
            logger.info(f"ℹ️  {file_path} not found, skipping...")
    logger.info("-" * 50)
    if updated_count > 0:
        logger.info(f"✅ Successfully updated {updated_count} file(s)")
    else:
        logger.info("ℹ️  No files were updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
