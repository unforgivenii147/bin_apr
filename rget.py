#!/data/data/com.termux/files/usr/bin/python
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from loguru import logger
from tqdm import tqdm

# ----------------------------
# Configuration
# ----------------------------
MAX_WORKERS = 8
MAX_RETRIES = 3
TIMEOUT = 60
OUTPUT_DIR = "downloads"
URLS_FILE = "urls.txt"
# Safe extensions (case-insensitive, regex patterns)
SAFE_EXTENSIONS = [
    r"\.ttf$",
    r"\.woff$",
    r"\.woff2$",
    r"\.eot$",
    r"\.otf$",
    r"\.min\.css$",
    r"\.min\.js$",
    r"\.css$",
    r"\.js$",
    r"\.pdf$",
    r"\.html?$",
    r"\.whl$",
    # Archives
    r"\.tar\.(gz|xz|zst|bz2|lzma|7z)$",
    r"\.zip$",
]
# Compile regex for speed
EXT_PATTERN = re.compile("|".join(SAFE_EXTENSIONS), re.IGNORECASE)


# ----------------------------
# Helper Functions
# ----------------------------
def sanitize_filename(name):
    """Clean filename: decode URL, remove invalid chars, limit length."""
    name = unquote(name)
    # Remove control chars, slashes, quotes, etc.
    name = re.sub(r'[<>:"|?*]', "_", name)
    # Limit length
    return name[:255].strip() or "downloaded_file"


def extract_filename(url):
    """
    Extract filename from URL, handling query params and paths.
    Examples:
        - 'font.woff2?v=1.2' → 'font.woff2'
        - 'style.min.css?ver=3.2' → 'style.min.css'
        - 'app.js?#hash' → 'app.js'
        - 'download.tar.gz?file=archive' → 'download.tar.gz'
    """
    parsed = urlparse(url)
    path = parsed.path
    # Strip query string & fragment from path
    filename = path.split("/")[-1] or "index.html"
    # Remove fragment from filename if present (e.g., 'file.js#hash' → 'file.js')
    filename = filename.split("#")[0]
    # Remove query string (e.g., 'file.css?v=1.2' → 'file.css')
    filename = filename.split("?")[0]
    # Decode URL encoding
    filename = sanitize_filename(filename)
    # Ensure it has an extension (fallback to .dat if none)
    if not re.search(r"\.[a-zA-Z0-9]+$", filename):
        filename += ".dat"
    return filename


def is_safe_extension(url):
    """Check if URL ends with a safe extension (case-insensitive)."""
    # Extract raw path first (including query params)
    parsed = urlparse(url)
    path = parsed.path
    # Get last segment of path
    filename = path.split("/")[-1]
    # Remove query string and fragment
    base_name = filename.split("?")[0].split("#")[0]
    return bool(EXT_PATTERN.search(base_name))


def get_filesize(url, session):
    """Get remote file size via HEAD request."""
    try:
        r = session.head(url, timeout=TIMEOUT, allow_redirects=True)
        r.raise_for_status()
        size = r.headers.get("Content-Length")
        return int(size) if size else None
    except Exception:
        return None


def download_one(url, session, output_dir, resume_from=None):
    """Download a single URL with resume support."""
    filename = extract_filename(url)
    filepath = os.path.join(output_dir, filename)
    # Determine resume offset
    offset = 0
    if resume_from and Path(filepath).exists():
        offset = Path(filepath).stat().st_size
        # If file is already complete, skip
        remote_size = get_filesize(url, session)
        if remote_size is not None and offset >= remote_size:
            return url, True, f"Already complete ({offset} bytes)"
    headers = {}
    if offset > 0:
        headers["Range"] = f"bytes={offset}-"
    try:
        with session.get(url, timeout=TIMEOUT, headers=headers, stream=True) as r:
            r.raise_for_status()
            content_length = int(r.headers.get("Content-Length", 0))
            total_size = content_length + offset if content_length else None
            mode = "ab" if offset else "wb"
            with Path(filepath).open(mode) as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
        return url, True, filepath
    except requests.exceptions.RequestException as e:
        if MAX_RETRIES > 0:
            return url, False, f"Retry needed: {e}"
        return url, False, str(e)


# ----------------------------
# Main Logic
# ----------------------------
def download_urls(urls, output_dir=OUTPUT_DIR):
    """Download all URLs in parallel, resuming where possible."""
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    safe_urls = [url for url in urls if is_safe_extension(url)]
    skipped = len(urls) - len(safe_urls)
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} URLs (not matching safe extensions).")
    if not safe_urls:
        print("❌ No valid URLs to download.")
        return
    print(f"🚀 Starting download of {len(safe_urls)} URLs...\n")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; ResumableDownloader/1.0)"})
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(download_one, url, session, output_dir): url for url in safe_urls}
        with tqdm(total=len(safe_urls), desc="Downloading", unit="file") as pbar:
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    url, success, result = future.result()
                    if success:
                        pbar.write(f"✅ {url.split('?')[0]} → {result}")
                    else:
                        pbar.write(f"❌ {url.split('?')[0]} failed: {result}")
                except Exception as e:
                    pbar.write(f"⚠️  Unexpected error for {url}: {e}")
                pbar.update(1)
    session.close()


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    try:
        with Path(URLS_FILE).open("r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"❌ Error: {URLS_FILE} not found.")
        sys.exit(1)
    if not urls:
        print(f"⚠️  No URLs found in {URLS_FILE}.")
        sys.exit(0)
    if len(sys.argv) > 1:
        URLS_FILE = sys.argv[1]
        print(f"Using input file: {URLS_FILE}")
        download_urls(urls)
    print("\n✅ All downloads completed.")
