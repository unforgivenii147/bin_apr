#!/data/data/com.termux/files/usr/bin/python
import os
import re


def compress_python_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Remove multiline strings (docstrings)
    # This regex handles """...""" and '''...''' and is careful about nested quotes
    content = re.sub(r'""".*?"""|\'\'\'.*?\'\'\'', "", content, flags=re.DOTALL)
    # Remove single-line comments
    content = re.sub(r"#.*", "", content)
    # Remove leading/trailing whitespace from each line and then remove empty lines
    lines = content.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    content = "\n".join(non_empty_lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def compress_python_files_in_directory(directory="."):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            filepath = os.path.join(directory, filename)
            print(f"Compressing {filepath}...")
            compress_python_file(filepath)
    print("Compression complete.")


if __name__ == "__main__":
    # You can change the directory here if needed
    compress_python_files_in_directory(".")
