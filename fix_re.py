#!/data/data/com.termux/files/usr/bin/python
"""
Fix regex patterns:
  - Add raw string prefix 'r' to the first argument of re.sub / re.search / re.find /
    re.findall / re.match if it is a non-raw string literal.
  - Then replace double backslashes '\\' with single backslashes '' inside that
    string literal.
Processes all .py files recursively from the current working directory.
Creates a .bak backup of each file before modifying it.
"""

import os
import sys
import shutil
import tokenize
import io

FUNC_NAMES = {"sub", "search", "find", "findall", "match", "finditer", "subn", "split"}
SKIP_TYPES = {
    tokenize.NL,
    tokenize.COMMENT,
    tokenize.NEWLINE,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.ENCODING,
    tokenize.TYPE_COMMENT,
}


def make_raw_and_fix(token_str):
    prefix_end = 0
    for ch in token_str:
        if ch in ('"', "'"):
            break
        prefix_end += 1
    else:
        return token_str
    prefix = token_str[:prefix_end]
    if "r" in prefix.lower():
        return token_str
    quote_char = token_str[prefix_end]
    if token_str[prefix_end : prefix_end + 3] == quote_char * 3:
        quote_len = 3
    else:
        quote_len = 1
    opening = quote_char * quote_len
    closing = opening
    content = token_str[prefix_end + quote_len : -quote_len]
    new_content = content.replace("\\\\", "\\")
    new_prefix = "r" + prefix
    return new_prefix + opening + new_content + closing


def process_file(filepath):
    """Process a single Python file. Returns True if modifications were made."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"Warning: cannot read {filepath}: {e}", file=sys.stderr)
        return False
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError as e:
        print(f"Warning: tokenizing error in {filepath}: {e}", file=sys.stderr)
        return False
    modifications = []
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        if tok.type == tokenize.NAME and tok.string == "re":
            j = i + 1
            while j < n and tokens[j].type in SKIP_TYPES:
                j += 1
            if j >= n:
                break
            if tokens[j].type == tokenize.OP and tokens[j].string == ".":
                k = j + 1
                while k < n and tokens[k].type in SKIP_TYPES:
                    k += 1
                if k >= n:
                    break
                if tokens[k].type == tokenize.NAME and tokens[k].string in FUNC_NAMES:
                    l = k + 1
                    while l < n and tokens[l].type in SKIP_TYPES:
                        l += 1
                    if l >= n:
                        break
                    if tokens[l].type == tokenize.OP and tokens[l].string == "(":
                        m = l + 1
                        while m < n and tokens[m].type in SKIP_TYPES:
                            m += 1
                        if m < n and tokens[m].type == tokenize.STRING:
                            str_tok = tokens[m]
                            new_str = make_raw_and_fix(str_tok.string)
                            if new_str != str_tok.string:
                                modifications.append((str_tok.start, str_tok.end, new_str))
        i += 1
    if not modifications:
        return False
    lines = source.splitlines(True)
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line))
    abs_mods = []
    for start, end, new_str in modifications:
        start_abs = line_offsets[start[0] - 1] + start[1]
        end_abs = line_offsets[end[0] - 1] + end[1]
        abs_mods.append((start_abs, end_abs, new_str))
    new_source = source
    for s, e, new in sorted(abs_mods, key=lambda x: x[0], reverse=True):
        new_source = new_source[:s] + new + new_source[e:]
    backup = filepath + ".bak"
    try:
        shutil.copy2(filepath, backup)
    except Exception as e:
        print(f"Warning: cannot create backup {backup}: {e}", file=sys.stderr)
        return False
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_source)
    print(f"Fixed {filepath}")
    return True


def main():
    root = "."
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".py"):
                filepath = os.path.join(dirpath, fn)
                process_file(filepath)


if __name__ == "__main__":
    main()
