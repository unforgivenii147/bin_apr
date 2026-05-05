#!/data/data/com.termux/files/usr/bin/python
import io
import os
from pathlib import Path
import runpy
from contextlib import redirect_stderr, redirect_stdout

from loguru import logger


def find_python_files(root_dir="."):
    """Recursively find all .py files."""
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        py_files.extend(
            os.path.join(dirpath, fname)
            for fname in filenames
            if fname.endswith(".py") and fname != Path(__file__).name
        )
    return sorted(py_files)


def run_script(script_path):
    """Run a Python script in isolation using runpy, capturing output."""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Running: {script_path}")
    logger.info(f"{'=' * 60}")
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Run script in its own namespace (isolated globals)
            # `run_name="__main__"` ensures `if __name__ == "__main__"` works
            runpy.run_path(script_path, run_name="__main__")
        logger.info("[✅ SUCCESS]")
    except SystemExit as e:
        logger.info(f"[⚠️ Script exited with code: {e.code}]")
    except Exception as e:
        logger.info(f"[❌ ERROR: {type(e).__name__}: {e}]")
    stdout_out = stdout_capture.getvalue()
    stderr_out = stderr_capture.getvalue()
    if stdout_out:
        logger.info("\n[STDOUT]:\n" + stdout_out)
    if stderr_out:
        logger.info("\n[STDERR]:\n" + stderr_out)
    logger.info()


def main():
    scripts = find_python_files(".")
    if not scripts:
        logger.info("No Python scripts found (excluding this script).")
        return
    logger.info(f"Found {len(scripts)} Python script(s). Starting execution...\n")
    for script in scripts:
        try:
            run_script(script)
        except Exception as e:
            logger.info(f"\n[FAILED TO RUN {script}]: {e}\n")
    logger.info("\n" + "=" * 60)
    logger.info("All scripts processed.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
