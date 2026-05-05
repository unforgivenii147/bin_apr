#!/data/data/com.termux/files/usr/bin/python
import subprocess
import sys
from pathlib import Path

from loguru import logger


def human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} TB"


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.info(
            f"[ERROR] Command failed: {' '.join(cmd)}",
            file=sys.stderr,
        )
        sys.exit(e.returncode)


def main() -> None:
    if len(sys.argv) < 2:
        logger.info(f"Usage: {sys.argv[0]} input.pdf")
        sys.exit(1)
    input_path = Path(sys.argv[1]).resolve()
    if not input_path.exists():
        logger.info(
            "Input file not found.",
            file=sys.stderr,
        )
        sys.exit(1)
    if input_path.suffix.lower() != ".pdf":
        logger.info(
            "Input must be a PDF file.",
            file=sys.stderr,
        )
        sys.exit(1)
    temp_qpdf = input_path.with_name(f"temp_qpdf_{input_path.name}")
    size_before = input_path.stat().st_size
    logger.info(f"Before : {human_size(size_before)}")
    qpdf_cmd = [
        "qpdf",
        "--linearize",
        "--object-streams=generate",
        str(input_path),
        str(temp_qpdf),
    ]
    run(qpdf_cmd)
    size_after = temp_qpdf.stat().st_size
    logger.info(f"After  : {human_size(size_after)}")
    diff = size_before - size_after
    sign = "-" if diff >= 0 else "+"
    if size_after < size_before:
        temp_qpdf.replace(input_path)
        logger.info(f"Saved  : {sign}{human_size(abs(diff))}")
    else:
        logger.info("original file is smaller")
        temp_qpdf.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
