#!/data/data/com.termux/files/usr/bin/python
from urllib.parse import urlparse
import regex as re
import sys

INPUT_FILE = sys.argv[1]


def normalize_url(u: str) -> str:
    u = u.strip()
    if not u:
        return ""

    if not re.match(r"^https?://", u, re.IGNORECASE):
        u = "https://" + u

    p = urlparse(u)

    scheme = "https"
    host = (p.netloc or "").lower()

    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    return f"{scheme}://{host}{path}"


def canonical_github_repo_root(normalized: str) -> str:
    """
    For GitHub, convert:
      /owner/repo
      /owner/repo/issues        -> keep /owner/repo
      /owner/repo/releases      -> keep /owner/repo
      /owner/repo/tree/...     -> keep /owner/repo
      /owner/repo/blob/...     -> keep /owner/repo
    """
    p = urlparse(normalized)
    if p.netloc.lower() not in ("github.com", "www.github.com"):
        return normalized

    segs = [s for s in p.path.split("/") if s]
    if len(segs) >= 2:
        owner, repo = segs[0], segs[1]
        return f"https://github.com/{owner}/{repo}"
    return f"https://github.com"


def canonical_other_root(normalized: str) -> str:
    """
    For non-GitHub:
      - keep scheme://host + first path segment (if present)
      - Example:
          https://example.com/a/b  => https://example.com/a
          https://example.com/a      => https://example.com/a
          https://example.com        => https://example.com/
    """
    p = urlparse(normalized)
    host = p.netloc.lower()
    path = p.path or "/"

    if host == "":
        return normalized

    segs = [s for s in path.split("/") if s]
    if not segs:
        return f"https://{host}/"

    first = segs[0]
    return f"https://{host}/{first}"


def canonical_root(normalized: str) -> str:
    return (
        canonical_github_repo_root(normalized)
        if "github.com" in normalized.lower()
        else canonical_other_root(normalized)
    )


def prune_subaddresses(urls):
    norm = [normalize_url(u) for u in urls]
    norm = [x for x in norm if x]

    best_by_root = {}
    for original in urls:
        n = normalize_url(original)
        if not n:
            continue
        root = canonical_root(n)
        if root not in best_by_root or len(n) < len(best_by_root[root]):
            best_by_root[root] = n

    kept = list(best_by_root.values())

    kept.sort(key=len)

    final = []
    for cand in kept:
        cand_p = urlparse(cand)
        cand_host = cand_p.netloc.lower()
        cand_path = (cand_p.path or "/").rstrip("/")
        if cand_path == "":
            cand_path = "/"

        is_sub = False
        for k in final:
            k_p = urlparse(k)
            if k_p.netloc.lower() != cand_host:
                continue
            k_path = (k_p.path or "/").rstrip("/")
            if k_path == "":
                k_path = "/"

            if cand_host == urlparse(k).netloc.lower():
                if cand_path == k_path:
                    is_sub = True
                    break
                if cand_path.startswith(k_path + "/"):
                    is_sub = True
                    break

        if not is_sub:
            final.append(cand)

    final.sort()
    return final


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pruned = prune_subaddresses(lines)

    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        for u in pruned:
            f.write(u + "\n")


if __name__ == "__main__":
    main()
