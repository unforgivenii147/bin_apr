#!/data/data/com.termux/files/usr/bin/python
import subprocess
import tempfile
from pathlib import Path
from dh import get_files

SVGCPATH = "/data/data/com.termux/files/home/.cargo/bin/svgcleaner"


def clean_single_svg(path):
    if not Path(path).exists():
        raise FileNotFoundError(msg)
    before = path.stat().st_size
    tmp_out_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_out:
            tmp_out_path = tmp_out.name
        subprocess.run(["svgcleaner", str(path), str(tmp_out_path)], check=True, capture_output=True)
        after = Path(tmp_out_path).stat().st_size
        if after != 0:
            Path(tmp_out_path).replace(path)
            size_change = before - after
            return (True, path, before, after, size_change)
        return (False, path, before, after, size_change)
    except subprocess.CalledProcessError as e:
        return (False, path, 0, 0, f"Error: {e.stderr.decode('utf-8')}")
    except Exception as e:
        return (False, path, 0, 0, f"Unexpected error: {e}")
    finally:
        if tmp_out_path and Path(tmp_out_path).exists():
            Path(tmp_out_path).unlink()


def clean_svg_dir(cwd, svgcleaner_path="svgcleaner"):
    svg_files = get_files(cwd, ext=[".svg"])
    if not svg_files:
        print("No SVG files found.")
        return
    total_before = 0
    total_after = 0
    total_saved = 0
    for path in svg_files:
        success, f, before, after, size_change = clean_single_svg(path)
        if success:
            print(f"Cleaned: {f}")
            print(f"  Before: {before} bytes, After: {after} bytes, Saved: {size_change} bytes")
            total_before += before
            total_after += after
            total_saved += size_change
        else:
            print(f"Failed to clean {f}: {size_change}")
    print("\n--- Summary ---")
    print(f"Total size saved: {total_saved} bytes")


if __name__ == "__main__":
    cwd = Path.cwd()
    clean_svg_dir(cwd)
