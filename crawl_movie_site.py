#!/data/data/com.termux/files/usr/bin/python


from utils import (
    OUTPUT_FILE,
    OUTPUT_FILE,
)

#!/data/data/com.termux/files/usr/bin/python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BASE_URL = "https://sr.moviesho.com/Series/"
OUTPUT_FILE = "movies.txt"

# Size limit in MB
MAX_SIZE_MB = 400

visited = set()
found_movies = []


def size_to_mb(size_str):
    """
    Convert size string like '343.7 MiB' or '296.0 MiB'
    to float MB value.
    """
    match = re.search(r"([\d.]+)\s*Mi?B", size_str)
    if match:
        return float(match.group(1))
    return None


def is_valid_movie(filename, size_mb):
    """
    Check if file matches:
    - mkv format
    - 480p or 720p
    - size under MAX_SIZE_MB
    """
    if not filename.lower().endswith(".mkv"):
        return False

    if not ("480p" in filename.lower() or "720p" in filename.lower()):
        return False

    if size_mb is None or size_mb >= MAX_SIZE_MB:
        return False

    return True


def crawl(url):
    if url in visited:
        return

    print(f"Crawling: {url}")
    visited.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to access {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract all rows
    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        link_tag = cols[0].find("a")
        if not link_tag:
            continue

        name = link_tag.text.strip()
        href = link_tag.get("href")
        size_text = cols[1].text.strip()

        full_url = urljoin(url, href)

        # Skip parent directory
        if "Parent directory" in name:
            continue

        # If it's a directory → recurse
        if href.endswith("/"):
            crawl(full_url)
        else:
            size_mb = size_to_mb(size_text)

            if is_valid_movie(name, size_mb):
                print(f"Found: {full_url} ({size_mb} MB)")
                found_movies.append(full_url)


if __name__ == "__main__":
    crawl(BASE_URL)

    # Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for movie in found_movies:
            f.write(movie + "\n")

    print(f"\n✅ Done. {len(found_movies)} movies saved to {OUTPUT_FILE}")
