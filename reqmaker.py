#!/data/data/com.termux/files/usr/bin/python
import subprocess
import sys
import re
from collections import defaultdict
from pathlib import Path


REQ = Path("requirements.txt")
def save_to_req(packages) -> None:

    def read_existing_requirements() -> set[str]:
        if not REQ.exists():
            return set()
        return { line.strip() for line in REQ.read_text(encoding="utf-8").splitlines() if line.strip() and (not line.startswith("#")) }
    existing = read_existing_requirements()
    merged = sorted(existing | set(packages))
    REQ.write_text("\n".join(merged) + "\n", encoding="utf-8")


def run_pip_check():
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stdout.strip() if e.stdout else ""


def parse_pip_check(output):
    pattern = re.compile(r"^(\S+)\s+.*requires\s+([^,]+),\s+which is not installed\.$", re.MULTILINE)
    missing_deps = defaultdict(list)
    for line in output.splitlines():
        match = pattern.match(line.strip())
        if match:
            requirer = match.group(1)
            missing_pkg = match.group(2).strip()
            missing_deps[missing_pkg].append(requirer)
    return missing_deps


def format_deptree(missing_deps):
    if not missing_deps:
        print("No missing dependencies found.")
        return
    print("required packages:")
    for pkg, requirers in sorted(missing_deps.items()):
        unique_requirers = sorted(set(requirers))
        requirers_str = ", ".join(unique_requirers)
        print(f"  - {pkg} --> {requirers_str}")


def main():
    output = run_pip_check()
    if not output:
        print("No output from `pip check`. Are you in a virtual environment?")
        return
    missing_deps = parse_pip_check(output)
    format_deptree(missing_deps)

    save_to_req(sorted(missing_deps.keys()))



if __name__ == "__main__":
    main()
