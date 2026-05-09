#!/data/data/com.termux/files/usr/bin/python
import io
import os
import runpy
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


def find_python_files(root_dir="."):
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        py_files.extend(
            os.path.join(dirpath, fname)
            for fname in filenames
            if fname.endswith(".py") and fname != Path(__file__).name
        )
    return sorted(py_files)


def run_script(script_path):
    print(f"\n{'=' * 60}")
    print(f"Running: {script_path}")
    print(f"{'=' * 60}")
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            runpy.run_path(script_path, run_name="__main__")
        print("[✅ SUCCESS]")
    except SystemExit as e:
        print(f"[⚠️ Script exited with code: {e.code}]")
    except Exception as e:
        print(f"[❌ ERROR: {type(e).__name__}: {e}]")
    stdout_out = stdout_capture.getvalue()
    stderr_out = stderr_capture.getvalue()
    if stdout_out:
        print("\n[STDOUT]:\n" + stdout_out)
    if stderr_out:
        print("\n[STDERR]:\n" + stderr_out)
    print()


def main():
    scripts = find_python_files(".")
    if not scripts:
        print("No Python scripts found (excluding this script).")
        return
    print(f"Found {len(scripts)} Python script(s). Starting execution...\n")
    for script in scripts:
        try:
            run_script(script)
        except Exception as e:
            print(f"\n[FAILED TO RUN {script}]: {e}\n")
    print("\n" + "=" * 60)
    print("All scripts processed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
