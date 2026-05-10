#!/data/data/com.termux/files/usr/bin/python

import stat
from pathlib import Path
from dh import get_filez
from loguru import logger

excluded = {"site-packages"}


def get_mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def denormalize_permissions(root_dir: str) -> None:
    DIR_PERM = 493
    FILE_PERM = 292
    for path in get_filez(root_dir):
        if "site-packages" in path.parts:
            continue
        try:
            current_perm = get_mode(path)
            if path.is_dir():
                if current_perm != DIR_PERM:
                    Path(path).chmod(DIR_PERM)
                    print(f"{path.name} {oct(current_perm)} : {oct(DIR_PERM)}")
            elif path.is_file():
                if current_perm != FILE_PERM:
                    Path(path).chmod(FILE_PERM)
                    print(
                        f"Set permissions for file: {path} from {oct(current_perm)} to {oct(FILE_PERM)}"
                    )
                try:
                    for encod in ["utf-8", "windows-1251"]:
                        with Path(path).open(errors="ignore",
                                             encoding=encod) as f:
                            f.read()
                except:
                    print(f"error reading {path.name}")
        except PermissionError as e:
            print(f"Permission denied: {path.name} ({e})")
        except FileNotFoundError:
            continue
        except OSError as e:
            print(f"OS error on {path.name}: {e}")


if __name__ == "__main__":
    denormalize_permissions(".")
