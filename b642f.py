#!/data/data/com.termux/files/usr/bin/python

import base64
import sys
from pathlib import Path

from dh import get_random_name

cleanup = False
cwd = Path.cwd()


def try_again(txt, fout):
    try:
        txt = txt[:-1]
        dbz = base64.b64decode(txt)
        fout.write_text(dbz)
    except:
        return


def clean_line(txt):
    cleaned: str = ""
    indx = txt.index("base64,") + 7
    cleaned = txt[indx:]
    if '"' in cleaned:
        end_indx = cleaned.index('"')
        cleaned = cleaned[:end_indx]
    elif " " in cleaned:
        end_indx = cleaned.index(" ")
        cleaned = cleaned[:end_indx]
    elif ")" in cleaned:
        end_indx = cleaned.index(")")
        cleaned = cleaned[:end_indx]
    return cleaned


0


def decode_base64_lines(input_path):
    success_count = 0
    error_count = 0
    failed = []
    remained = []
    output_path = Path(f"{Path(input_path).name}_{get_random_name()}.bin")
    try:
        with Path(input_path).open(encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                output_path = Path(f"{Path(input_path).name}_{get_random_name()}.bin")
                if not line:
                    continue
                if "base64," in line:
                    line = clean_line(line)
                try:
                    decoded_bytes = base64.b64decode(line.strip())
                    Path(output_path).write_bytes(decoded_bytes)
                    success_count += 1
                except Exception as e:
                    print(f"✗ Line {i:4d} failed: {e}")
                    error_count += 1
                    failed.append(i)
                    remained.append(line)
        print(f"Failed : {error_count} lines")
        print(failed)
        if success_count > 0:
            print(f"done")
    except FileNotFoundError:
        print(f"file not found: {input_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")


#    if cleanup:
#        with Path(input_path).open("w", encoding="utf-8") as fo:
#            fo.writelines(f"{k}\n" for k in remained)


if __name__ == "__main__":
    INPUT_FILE = sys.argv[1]
    decode_base64_lines(INPUT_FILE)
