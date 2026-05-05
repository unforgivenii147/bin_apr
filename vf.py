#!/data/data/com.termux/files/usr/bin/python
import sys
import re
from pathlib import Path


major, minor, _, _, _ = sys.version_info
py_version = f"{major}{minor}"

whl_directory = Path()
whl_pattern = re.compile(
    r"(?P<name>[\w\-]+)-(?P<version>[\d\.]+(?:-\d{8})?)-(?P<python>py3-none-any|cp37-abi3-linux_armv8l|cp{py_version}-cp{py_version}-linux_armv8l|cp{py_version}-cp{py_version}-linux_arm|py3-none-linux_armv8l)\.whl"
)


def cleanup_wheels(whl_dir: Path):
    deleted_files = 0
    latest_versions = {}
    for file_path in whl_dir.glob("*.whl"):
        file_name = file_path.name
        matchz = whl_pattern.match(file_name)
        if matchz:
            package_name = matchz.group("name")
            version = matchz.group("version")
            python_variant = matchz.group("python")
            if "-" in version:
                date_part = version.split("-")[-1]
                if package_name not in latest_versions or date_part > latest_versions[package_name][0]:
                    latest_versions[package_name] = (date_part, version, file_path)

    for file_path in whl_dir.glob("*.whl"):
        file_name = file_path.name
        matchz = whl_pattern.match(file_name)
        if matchz:
            package_name = matchz.group("name")
            version = matchz.group("version")
            python_variant = match.group("python")
            if (package_name == "pycryptodome" and python_variant == "py3-none-any") or (
                package_name == "matplotlib" and python_variant == "py3-none-any"
            ):
                file_path.unlink()
                print(f"Deleted: {file_name}")
                deleted_files += 1
            elif "-" in version:
                date_part = version.split("-")[-1]
                if (package_name in latest_versions and latest_versions[package_name][0] != date_part) or (
                    package_name in latest_versions and latest_versions[package_name][2] != file_path
                ):
                    file_path.unlink()
                    print(f"Deleted: {file_name}")
                    deleted_files += 1
    return deleted_files


if __name__ == "__main__":
    whl_files_paths = list(whl_directory.glob("*.whl"))
    deleted_files = cleanup_wheels(whl_directory)
    print(f"Number of files deleted: {deleted_files}")
