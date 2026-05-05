#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

from loguru import logger


def main() -> None:
    hist_file = Path.home() / ".bash_history"
    if not hist_file.exists():
        logger.info("~/.bash_history does not exist.")
        return
    with hist_file.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    seen = set()
    unique_lines = []
    histlen = len(lines)
    logger.info(f"history length: {histlen}")
    for line in lines:
        stripped = line.rstrip("\n")
        if stripped not in seen:
            seen.add(stripped)
            unique_lines.append(line)
    with hist_file.open("w", encoding="utf-8") as f:
        f.writelines(unique_lines)
    logger.info(f"{histlen - len(unique_lines)} lines removed")


if __name__ == "__main__":
    main()
