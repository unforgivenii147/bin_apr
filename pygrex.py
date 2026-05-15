#!/data/data/com.termux/files/usr/bin/python


#!/data/data/com.termux/files/usr/bin/python
import sys
import re

if len(sys.argv) != 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, "r", encoding="utf-8") as f:
    lines = [line.rstrip("\n") for line in f]

# Escape each line so special regex characters are treated literally
pattern = r"^(?:%s)$" % "|".join(re.escape(line) for line in lines)

print(pattern)
