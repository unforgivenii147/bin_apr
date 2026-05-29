#!/data/data/com.termux/files/usr/bin/python
import json
import re
import sys


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string (uppercase, no spaces)."""
    return data.hex().upper()


def parse_magic_line(line: str):
    """
    Parse a magic rule line like:
        >0=�<?xml
        1>0=�-//OASIS...
    Returns (offset, mask, value_bytes) or None if invalid.
    """
    # Match: optional rule_index, '>', offset, '=', rest (value)
    # e.g., "1>0=abc", ">0=xyz", "0>2=..."
    match = re.match(r"^(?:(\d+?)>)?(\d+)=", line)
    if not match:
        return None
    rule_index = int(match.group(1)) if match.group(1) else None
    offset = int(match.group(2))
    value_part = line[match.end() :]  # remaining bytes as string
    # The tricky part: value_part may contain binary/unprintable chars.
    # Best approach: if input file is binary-safe, read as Latin-1 (1:1 mapping)
    # But here we assume the line is given as a str with raw bytes as Latin-1 chars.
    # So encode using 'latin-1' to get original bytes.
    try:
        value_bytes = value_part.encode("latin-1")
    except UnicodeEncodeError:
        # Fallback: if already bytes, or if UTF-8 with errors, try replace
        # But prefer latin-1 above — it never fails.
        value_bytes = value_part.encode("latin-1", errors="replace")
    return {"rule_index": rule_index, "offset": offset, "value_bytes": value_bytes, "hex": bytes_to_hex(value_bytes)}


def parse_magic_file(filepath: str, encoding="latin-1"):
    """
    Parse a magic-file-like input.
    Returns dict: {mimetype: [rules...]}
    """
    result = {}
    current_mimetype = None
    with open(filepath, "rb") as f:
        raw_lines = f.readlines()
    # Decode each line using latin-1 (preserves bytes 0-255)
    lines = [line.decode("latin-1", errors="replace") for line in raw_lines]
    for line in lines:
        line = line.rstrip("\n\r")
        if not line.strip():
            continue  # skip empty lines
        # Section header: [mimetype]
        if line.startswith("[") and line.endswith("]"):
            current_mimetype = line[1:-1].strip()
            if current_mimetype not in result:
                result[current_mimetype] = []
            continue
        if line.startswith("#") or line.startswith("!"):
            continue
        if current_mimetype is None:
            # Optional: warn or skip
            print(f"Warning: rule outside section: {line!r}", file=sys.stderr)
            continue
        parsed = parse_magic_line(line)
        if parsed:
            # Build rule dict
            rule = {"offset": parsed["offset"], "value_hex": parsed["hex"], "length": len(parsed["value_bytes"])}
            if parsed["rule_index"] is not None:
                rule["rule_index"] = parsed["rule_index"]
            result[current_mimetype].append(rule)
        else:
            print(f"Warning: Failed to parse rule: {line!r}", file=sys.stderr)
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python magic_to_json.py <magic_file> [output.json]", file=sys.stderr)
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    data = parse_magic_file(input_file)
    json_output = json.dumps(data, indent=2, ensure_ascii=False)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"✅ Written to {output_file}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
