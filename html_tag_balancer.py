#!/data/data/com.termux/files/usr/bin/python
"""
HTML Tag Balancer & Validator
Checks HTML files recursively for unbalanced tags and optionally fixes them in-place.
- Self-closing tags (e.g., <meta>, <link>, <img>, <br>, etc.) are respected.
- Missing closing tags are appended at the end of the file (after </body> or </html> if present).
- Unexpected closing tags (without matching open) are removed.
- Uses pathlib and html.parser (no regex).
"""

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path

# Standard self-closing (void) elements per HTML5 spec
VOID_ELEMENTS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
)


class TagBalanceChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []  # list of (tag_name, start_tag_pos)
        self.errors = []  # list of (type, tag, pos)
        self.raw_source = ""
        self.fix_needed = False

    def set_source(self, source: str):
        self.raw_source = source

    def handle_starttag(self, tag, attrs):
        if tag.lower() in VOID_ELEMENTS:
            return  # self-closing; no match needed
        self.stack.append((tag.lower(), self.getpos()))

    def handle_endtag(self, tag):
        tag = tag.lower()
        # Unexpected closing tag (no matching open)
        if not self.stack or self.stack[-1][0] != tag:
            # Find if there's *any* unmatched open of this tag (not just top of stack)
            # If found, pop it (to allow later mismatched pairs to be caught)
            try:
                idx = len(self.stack) - 1
                while idx >= 0 and self.stack[idx][0] != tag:
                    idx -= 1
                if idx >= 0:
                    self.stack.pop(idx)  # "fix" by ignoring mismatch
                else:
                    # truly unexpected: no open tag of this type
                    self.errors.append(("unexpected_closing", tag, self.getpos()))
                    self.fix_needed = True
            except Exception:
                # fallback: just record error
                self.errors.append(("unexpected_closing", tag, self.getpos()))
                self.fix_needed = True
        else:
            self.stack.pop()

    def handle_startendtag(self, tag, attrs):
        # <img/> or <meta/> — treated same as starttag (self-closing)
        pass  # already handled by handle_starttag in Python 3.4+ (but safe to ignore)


def check_html_file(path: Path) -> tuple[bool, list[str]]:
    """Check one file; returns (is_balanced, list_of_issues)."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, [f"⚠️  Could not read file: {e}"]
    parser = TagBalanceChecker()
    parser.set_source(source)
    try:
        parser.feed(source)
    except Exception as e:
        return False, [f"⚠️  Parsing error: {e}"]
    # Remaining open tags = missing closings
    missing_closings = [f"Missing </{tag}> (opened at line {pos[0]}, col {pos[1]})" for tag, pos in parser.stack]
    unexpected_closings = [f"Unexpected </{tag}> at line {pos[0]}, col {pos[1]}" for _, tag, pos in parser.errors]
    issues = missing_closings + unexpected_closings
    is_balanced = len(issues) == 0
    return is_balanced, issues


def fix_html_file(path: Path) -> bool:
    """Fix one file in-place."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"❌ Cannot read '{path}': {e}", file=sys.stderr)
        return False
    parser = TagBalanceChecker()
    parser.set_source(source)
    try:
        parser.feed(source)
    except Exception as e:
        print(f"❌ Parsing error in '{path}': {e}", file=sys.stderr)
        return False
    # Collect tags to remove (unexpected closings)
    # We'll rebuild the source *without* those closing tags
    # Strategy: rebuild token-by-token (simplest reliable way without regex)
    # → But to avoid full re-tokenization + re-render, we'll use a simpler approach:
    #   - Replace unexpected closings by empty string (using positions)
    #   - Append missing closings at end (after </body> or </html> if found)
    # Build list of unexpected closing tag positions to remove
    remove_ranges = []
    for _, tag, pos in parser.errors:
        line, col = pos
        # Find the string "</tag>" starting at that position
        # But position is (line, col) in parser's view → convert to byte/char index
        # Easier: parse again while tracking indices
        pass  # We'll use a safer, cleaner method below
    # ✅ Better approach: re-tokenize *with* start/end positions
    from html.parser import HTMLParseError

    class TagScanner(HTMLParser):
        def __init__(self, source):
            super().__init__()
            self.source = source
            self.chars = list(source)  # char list for indexing
            self.tokens = []  # list of (type, tag, start, end)

        def get_char_pos(self, line, col):
            # Convert (line, col) to absolute char index
            # line is 1-based, col is 0-based
            lines = self.source.splitlines(keepends=True)
            idx = 0
            for i in range(line - 1):
                if i < len(lines):
                    idx += len(lines[i])
            return idx + col

        def handle_starttag(self, tag, attrs):
            if tag.lower() not in VOID_ELEMENTS:
                pos = self.getpos()
                start = self.get_char_pos(*pos)
                # Find end of starttag: look for '>' after start
                end = self.source.find(">", start)
                if end != -1:
                    self.tokens.append(("start", tag, start, end + 1))
                else:
                    self.tokens.append(("start", tag, start, start + len(f"<{tag}")))

        def handle_endtag(self, tag):
            pos = self.getpos()
            # Find start of </tag> in source
            tag_str = f"</{tag}>"
            start = self.source.find(tag_str, self.get_char_pos(*pos))
            if start == -1:
                # Try approximate (e.g., case-insensitive, extra whitespace)
                import re

                m = re.search(rf"</\s*{tag}\s*>", self.source, re.IGNORECASE)
                if m:
                    start = m.start()
            if start != -1:
                self.tokens.append(("end", tag, start, start + len(tag_str)))

        def handle_startendtag(self, tag, attrs):
            pos = self.getpos()
            start = self.get_char_pos(*pos)
            end = self.source.find(">", start)
            if end != -1:
                self.tokens.append(("startend", tag, start, end + 1))

    scanner = TagScanner(source)
    try:
        scanner.feed(source)
    except Exception:
        pass  # fallback to simple method
    # Build new source by removing unexpected closing tags
    # Collect ranges to remove: (start, end)
    ranges_to_remove = []
    for _, tag, pos in parser.errors:
        # Find position of "</tag>" near parser's reported position
        line, col = pos
        base_idx = 0
        for _ in range(line - 1):
            # skip lines
            idx = source.find("\n", base_idx)
            if idx == -1:
                break
            base_idx = idx + 1
        # Now look for "</tag>" starting near base_idx + col
        target = f"</{tag}>"
        search_start = max(0, base_idx + col - 5)
        idx = source.find(target, search_start)
        if idx != -1:
            ranges_to_remove.append((idx, idx + len(target)))
        else:
            # Try case-insensitive
            target_lower = target.lower()
            idx = source.lower().find(target_lower, search_start)
            if idx != -1:
                ranges_to_remove.append((idx, idx + len(target)))
    # Merge overlapping ranges (just in case)
    ranges_to_remove.sort()
    merged = []
    for r in ranges_to_remove:
        if merged and r[0] <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], r[1]))
        else:
            merged.append(r)
    # Build new source excluding removed ranges
    new_source = source
    if merged:
        # Remove ranges in reverse order to preserve indices
        for start, end in reversed(merged):
            new_source = new_source[:start] + new_source[end:]
    # Append missing closing tags
    missing_tags = [tag for tag, _ in parser.stack]
    # Close in reverse order (LIFO)
    missing_tags.reverse()
    # Try to insert after </body> or </html>
    insert_pos = len(new_source)
    for end_tag in ("</body>", "</html>"):
        idx = new_source.rfind(end_tag)
        if idx != -1:
            # Find end of tag
            idx_end = new_source.find(">", idx)
            if idx_end != -1:
                insert_pos = idx_end + 1
            else:
                insert_pos = idx + len(end_tag)
            break
    if missing_tags:
        closing_html = "".join(f"</{tag}>" for tag in missing_tags)
        new_source = new_source[:insert_pos] + closing_html + new_source[insert_pos:]
    # Write back
    try:
        path.write_text(new_source, encoding="utf-8")
        return True
    except Exception as e:
        print(f"❌ Cannot write '{path}': {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check and optionally fix HTML tag balance in files recursively.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-a",
        "--autofix",
        action="store_true",
        help="Fix files in-place (append missing closing tags, remove unexpected ones)",
    )
    args = parser.parse_args()
    current_dir = Path(".")
    html_files = list(current_dir.rglob("*.html")) + list(current_dir.rglob("*.htm"))
    html_files = sorted(set(html_files))  # dedupe & sort
    if not html_files:
        print("ℹ️  No HTML files found in current directory (recursively).")
        return
    print(f"🔍 Found {len(html_files)} HTML file(s). Checking...")
    fixed_count = 0
    problem_count = 0
    for fpath in html_files:
        is_balanced, issues = check_html_file(fpath)
        if is_balanced:
            print(f"✅ {fpath} — OK")
        else:
            problem_count += 1
            print(f"❌ {fpath} — {len(issues)} issue(s):")
            for issue in issues:
                print(f"   • {issue}")
            if args.autofix:
                if fix_html_file(fpath):
                    print(f"   🔧 Fixed in-place.")
                    fixed_count += 1
                else:
                    print(f"   ⚠️  Fix failed.")
    print()
    print(f"Summary: {len(html_files) - problem_count} OK, {problem_count} with issues")
    if args.autofix:
        print(f"   → Fixed {fixed_count} file(s) in-place.")


if __name__ == "__main__":
    main()
