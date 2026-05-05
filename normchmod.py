#!/data/data/com.termux/files/usr/bin/python
import stat
from pathlib import Path


def get_mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def normalize_permissions(homedir) -> None:
    DIR_PERM = 0o775
    FILE_PERM = 0o664
    for path in homedir.rglob("*"):
        try:
            current_perm = get_mode(path)
            if path.is_dir():
                if current_perm != DIR_PERM:
                    Path(path).chmod(DIR_PERM)
                    print(f"{path.name} {oct(current_perm)} : {oct(DIR_PERM)}")
            elif path.is_file():
                if path.suffix == ".sh":
                    print(current_perm)
                if current_perm != FILE_PERM:
                    if path.parent.name != "bin" and path.suffix != ".sh":
                        path.chmod(FILE_PERM)
                    print(f"{path.relative_to(cwd)}: {oct(current_perm)} --> {oct(FILE_PERM)}")
                try:
                    for encod in [
                        "utf-8",
                        "windows-1251",
                    ]:
                        with Path(path).open(errors="ignore", encoding=encod) as f:
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
    cwd = Path.cwd()
    normalize_permissions(cwd)
