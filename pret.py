#!/data/data/com.termux/files/usr/bin/python

import sys
from collections import deque
from collections.abc import Callable, Iterable
from contextlib import suppress as _suppress
from multiprocessing import get_context
from os import scandir as os_scandir
from pathlib import Path
from subprocess import DEVNULL as subprocess_DEVNULL
from subprocess import TimeoutExpired as subprocess_TimeoutExpired
from subprocess import run as subprocess_run
from tempfile import NamedTemporaryFile as _tmpfile
from time import sleep as _sleep
from typing import Any
from dh import cprint

CHUNK_SIZE = 32768
MAX_WORKERS: int = 4
MAX_IN_FLIGHT = 4
SKIP_DIRS = {".git"}


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


def get_files(
    path: str | Path, include_hidden: bool = True, recursive: bool = True, extensions: list[str] | None = None
) -> list[Path]:
    path = Path(path)
    out = []
    if recursive:
        stack = [path]
        while stack:
            current = stack.pop()
            try:
                with os_scandir(current) as it:
                    for entry in it:
                        name = entry.name
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            if name not in SKIP_DIRS:
                                stack.append(Path(entry.path))
                            continue
                        if extensions is not None and (not any((entry.name.endswith(ext) for ext in extensions))):
                            continue
                        out.append(Path(entry.path))
            except (PermissionError, FileNotFoundError):
                continue
    return out


def gsz(path: str | Path) -> int:
    path = Path(path)
    total_size = 0
    if not path.exists():
        return 0
    if path.is_file():
        try:
            total_size = path.stat().st_size
        except OSError:
            return 0
    elif path.is_dir():
        for entry in os_scandir(path):
            try:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += gsz(entry.path)
            except OSError:
                continue
    return total_size


def mpf3(
    func: Callable[[Any], Any],
    items: Iterable[Any],
    max_in_flight: int = 4,
    num_processes: int = 4,
    context_method: str = "spawn",
) -> None:
    with get_context(context_method).Pool(num_processes) as p:
        pending = deque()
        for item in items:
            pending.append(p.apply_async(func, (item,)))
            if len(pending) >= max_in_flight:
                pending.popleft().get()
        while pending:
            pending.popleft().get()


def runcmd(
    cmd: list[str], run_silently: bool = False, show_output: bool = True, timeout: float | None = None
) -> tuple[int, str, str]:
    if not cmd:
        msg = "cmd must be a non-empty list (e.g., ['ls', '-l'])"
        raise ValueError(msg)
    try:
        if run_silently:
            result = subprocess_run(cmd, stdout=subprocess_DEVNULL, stderr=subprocess_DEVNULL, timeout=timeout)
            return (result.returncode, "", "")
        result = subprocess_run(cmd, capture_output=True, text=True, timeout=timeout)
        stdout, stderr = (result.stdout, result.stderr)
        if show_output:
            if stdout:
                sys.stdout.write(stdout)
                sys.stdout.flush()
            if stderr:
                sys.stderr.write(stderr)
                sys.stderr.flush()
        return (result.returncode, stdout, stderr)
    except FileNotFoundError:
        msg = f"Command not found: '{cmd[0]}'"
        if show_output and (not run_silently):
            print(msg, file=sys.stderr)
        return (127, "", msg)
    except PermissionError:
        msg = f"Permission denied: '{cmd[0]}'"
        if show_output and (not run_silently):
            print(msg, file=sys.stderr)
        return (126, "", msg)
    except subprocess_TimeoutExpired:
        msg = f"Command timed out after {timeout}s: {' '.join(cmd)}"
        if show_output and (not run_silently):
            print(msg, file=sys.stderr)
        return (124, "", msg)
    except Exception as e:
        msg = f"Unexpected error running '{cmd[0]}': {e}"
        if show_output and (not run_silently):
            print(msg, file=sys.stderr)
        return (1, "", msg)


def process_file(fp):
    before = fp.stat().st_size
    cmd = ["prettier", "--write", "--with-node-modules", str(fp)]
    code, _out, _err = runcmd(cmd, show_output=False)
    if not code:
        after = fp.stat().st_size
        diffsize = before - after
        if diffsize:
            ratio = (before - after) / before * 100
        if not diffsize:
            cprint("[NO CHANGE] ", "green", end="")
            cprint(f"{fp.name}", "white")
        elif diffsize < 0:
            cprint(f"[OK] {fp.name} ", "white", end="")
            cprint(f" + {fsz(diffsize)}", "green")
        elif diffsize > 0:
            cprint(f"[OK] {fp.name} ", "white", end="")
            cprint(f" - {fsz(diffsize)} {ratio:.1f}%", "cyan")
        return True
    cprint(f"[ERROR] {fp.name}", "red")
    return False


def main() -> None:
    cwd = Path.cwd()
    args = sys.argv[1:]
    files = (
        [Path(arg) for arg in args]
        if args
        else get_files(
            cwd,
            extensions=[
                ".md",
                ".js",
                ".css",
                ".ts",
                ".tsx",
                ".jsx",
                ".json",
                ".html",
                ".cjs",
                ".cts",
                ".mts",
                ".mjs",
                ".coffee",
                ".yaml",
                ".yml",
                ".scss",
                ".markdown",
            ],
        )
    )
    if not files:
        print("no file found.")
        sys.exit(1)
    mpf3(process_file, files)


if __name__ == "__main__":
    main()
