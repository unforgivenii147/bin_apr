#!/data/data/com.termux/files/usr/bin/python


from utils import (
    main,
    main,
    main,
    main,
    INPUT_FILE,
    main,
    main,
    main,
    main,
    main,
    INPUT_FILE,
    main,
)

#!/data/data/com.termux/files/usr/bin/python
from urllib.parse import urlparse
import re
import sys

INPUT_FILE = sys.argv[1]


def normalize_url(u: str) -> str:
    """Normalize a URL: ensure scheme, lowercase host, trim trailing slash on path (except root)."""
    u = u.strip()
    if not u:
        return ""
    if not re.match(r"^https?://", u, re.IGNORECASE):
        u = "https://" + u
    p = urlparse(u)
    scheme = p.scheme.lower()
    host = (p.netloc or "").lower()
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return f"{scheme}://{host}{path}"


def canonical_root(normalized: str) -> str:
    """
    Return the canonical root of a normalized URL:
      - GitHub: /owner/repo (ignores /issues, /tree, /blob, etc.)
      - Others: scheme://host/first_segment (or scheme://host/ if no path)
    """
    p = urlparse(normalized)
    scheme = p.scheme
    host = p.netloc.lower()
    if not host:
        return normalized

    if host in ("github.com", "www.github.com"):
        segs = [s for s in (p.path or "/").split("/") if s]
        if len(segs) >= 2:
            owner, repo = segs[0], segs[1]
            return f"https://github.com/{owner}/{repo}"
        return f"https://github.com"

    segs = [s for s in (p.path or "/").split("/") if s]
    if not segs:
        return f"{scheme}://{host}/"
    first = segs[0]
    return f"{scheme}://{host}/{first}"


def is_subsumed(candidate: str, existing: str) -> bool:
    """
    Check if `candidate` URL is a subpath of `existing` on the same host.
    Returns True if candidate is redundant (i.e., covered by existing).
    """
    cand_p = urlparse(candidate)
    ex_p = urlparse(existing)
    if cand_p.netloc.lower() != ex_p.netloc.lower():
        return False
    cand_path = (cand_p.path or "/").rstrip("/") or "/"
    ex_path = (ex_p.path or "/").rstrip("/") or "/"
    if cand_path == ex_path:
        return True
    if ex_path == "/" and cand_path != "/":
        return True
    if cand_path.startswith(ex_path + "/"):
        return True
    return False


def prune_subaddresses(urls):
    # Step 1: Normalize all and filter empties
    normalized = [normalize_url(u) for u in urls]
    normalized = [u for u in normalized if u]
    best_by_root = {}
    for n in normalized:
        root = canonical_root(n)
        if root not in best_by_root or len(n) < len(best_by_root[root]):
            best_by_root[root] = n
    kept = sorted(best_by_root.values(), key=len)
    final = []
    for cand in kept:
        # Skip if subsumed by any already-kept URL
        if any(is_subsumed(cand, k) for k in final):
            continue
        final.append(cand)
    final.sort()
    return final


def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{INPUT_FILE}': {e}", file=sys.stderr)
        sys.exit(1)
    pruned = prune_subaddresses(lines)
    try:
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            for url in pruned:
                f.write(url + "\n")
    except IOError as e:
        print(f"Error writing to file '{INPUT_FILE}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
