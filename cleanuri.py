#!/data/data/com.termux/files/usr/bin/python
"""
Recursively extract embedded base64 data URIs from .css, .js, and .html files
in the current directory, save the decoded assets to an `assets/` folder,
and replace the URIs with relative links.
Each asset is named after the SHA‑256 hash of the full data URI.
Duplicate assets are only saved once.
"""

import base64
import hashlib
import mimetypes
import os
import re
from pathlib import Path

# Pattern for base64 data URIs:
#   data:[<mime>][;parameter=value...];base64,<base64-data>
DATA_URI_PATTERN = re.compile(
    r"data:"
    r"(?P<mime>[^;,]*)"  # MIME type (optional)
    r"(?P<params>(?:;[^;,]+=[^;,]+)*)"  # additional parameters (optional)
    r";base64,"
    r"(?P<data>[A-Za-z0-9+/=]+)"  # base64 payload
)


def get_extension(mime: str) -> str:
    """Return a file extension (with leading dot) for the given MIME type."""
    if mime:
        # Try the standard library first
        ext = mimetypes.guess_extension(mime)
        if ext:
            return ext
        # Fallback: use the subtype (e.g., "font/ttf" -> ".ttf")
        parts = mime.split("/")
        if len(parts) == 2 and parts[1]:
            return f".{parts[1]}"
    # Unknown or missing MIME → binary
    return ".bin"


def process_file(file_path: Path, assets_dir: Path, processed: dict) -> None:
    """
    Find all data URIs in *file_path*, save the decoded assets, and
    replace the URIs with relative links to the `assets/` directory.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"⚠ Skipping {file_path}: {e}")
        return
    # Relative path from the file's folder to the top‑level assets folder
    rel_to_assets = Path(os.path.relpath(assets_dir, file_path.parent))

    def replace_match(match: re.Match) -> str:
        full = match.group(0)  # entire data URI
        mime = match.group("mime") or None
        data_b64 = match.group("data")
        # Unique identifier for the asset (SHA‑256 of the full URI)
        hash_digest = hashlib.sha256(full.encode()).hexdigest()
        # If not seen yet, decode and write the asset
        if hash_digest not in processed:
            ext = get_extension(mime)
            filename = f"{hash_digest}{ext}"
            asset_path = assets_dir / filename
            try:
                binary = base64.b64decode(data_b64)
            except Exception as e:
                print(f"⚠ Base64 decode error in {file_path}: {e}  – keeping original.")
                return full
            if not asset_path.exists():
                asset_path.write_bytes(binary)
                print(f"✔ Saved asset: {asset_path}")
            processed[hash_digest] = filename
        else:
            filename = processed[hash_digest]
        # Relative link to the asset
        link = rel_to_assets / filename
        return link.as_posix()

    # Perform the replacements
    new_content = DATA_URI_PATTERN.sub(replace_match, content)
    if new_content != content:
        file_path.write_text(new_content, encoding="utf-8")
        print(f"✎ Updated {file_path}")


def main():
    """Main entry point: walk the current directory and process target files."""
    mimetypes.init()  # initialise MIME‑to‑extension mappings
    assets_dir = Path("assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    processed = {}  # hash -> filename (inside assets/)
    current_dir = Path(".")
    for file_path in current_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in (".css", ".js", ".html"):
            process_file(file_path, assets_dir, processed)
    print("Done.")


if __name__ == "__main__":
    main()
