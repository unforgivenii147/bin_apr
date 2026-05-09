#!/data/data/com.termux/files/usr/bin/python

import base64
import sys
from pathlib import Path
from dh import get_random_name

cleanup = False


def try_again(txt, fin, fout):
    try:
        txt = txt[1:]
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
    elif ")" in cleaned:
        end_indx = cleaned.index(")")
        cleaned = cleaned[:end_indx]
    return cleaned


def decode_base64_lines(input_path, output_folder="decoded_files"):
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)
    success_count = 0
    error_count = 0
    failed = []
    remained = []
    output_filename = f"{Path(input_path).name}{get_random_name()}.bin"
    output_path = output_dir / output_filename
    try:
        with Path(input_path).open(encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                if "base64," in line:
                    line = clean_line(line)
                try:
                    decoded_bytes = base64.b64decode(line.strip())
                    Path(output_path).write_bytes(decoded_bytes)
                    success_count += 1
                except Exception as e:
                    try_again(line, input_path, output_path)
                    print(f"✗ Line {i:4d} failed: {e}")
                    error_count += 1
                    failed.append(i)
                    remained.append(line)
        print(f"Failed : {error_count} lines")
        print(failed)
        if success_count > 0:
            print(f"Files saved in: {output_dir.resolve()}")
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    if cleanup:
        with Path(input_path).open("w", encoding="utf-8") as fo:
            fo.writelines((f"{k}\n" for k in remained))


if __name__ == "__main__":
    INPUT_FILE = sys.argv[1]
    OUTPUT_FOLDER = "output"
    decode_base64_lines(INPUT_FILE, OUTPUT_FOLDER)
