#!/data/data/com.termux/files/usr/bin/python


from utils import (
    main,
    main,
    main,
    main,
    main,
    main,
    main,
    main,
    main,
    main,
)

#!/data/data/com.termux/files/usr/bin/python
import sys
import os
import html


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} input.html [output.html]", file=sys.stderr)
        sys.exit(1)

    fn = sys.argv[1]
    text = ""
    with open(fn, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    with open(fn, "w", encoding="utf-8") as f:
        f.write(html.unescape(text))


if __name__ == "__main__":
    main()
