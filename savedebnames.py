#!/data/data/com.termux/files/usr/bin/python
import subprocess
from pathlib import Path
from loguru import logger


def save_installed_packages(output_file="installed.txt"):
    try:
        result = subprocess.run(
            [
                "dpkg-query",
                "-f",
                "${binary:Package}\n",
                "-W",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        installed_packages = result.stdout.splitlines()
        Path(output_file).write_text("\n".join(installed_packages), encoding="utf-8")
        logger.info(f"Installed package names saved to '{output_file}'")
    except FileNotFoundError:
        logger.info("Error: dpkg-query command not found. Are you running this script on a Debian-based system?")
    except subprocess.CalledProcessError as e:
        logger.info(f"Error: Failed to retrieve installed packages. {e}")
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    save_installed_packages()
