#!/data/data/com.termux/files/usr/bin/python

import html
import os
from pathlib import Path
from loguru import logger

FONT_EXTENSIONS = (".ttf", ".otf", ".woff", ".woff2", ".eot")
SAMPLE_TEXT = "Lorem ipsum dolor sit amet\nهنر برتر از گوهر آمد پدید"
OUTPUT_FILE = "fontpreview.html"
HTML_START = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>Font Preview</title>\n<style>\nbody {\n  background:\n  color:\n  font-family: system-ui, sans-serif;\n  margin: 0 auto;\n  padding: 20px;\n  max-width: 960px;\n}\nh1 {\n  margin-top: 40px;\n  font-size: 1.6em;\n  border-bottom: 1px solid\n  padding-bottom: .3em;\n  color:\n}\ntextarea {\n  width: 100%;\n  height: 100px;\n  padding: 12px;\n  margin-top: 6px;\n  border-radius: 8px;\n  border: 1px solid\n  font-size: 1.1em;\n  box-sizing: border-box;\n  resize: vertical;\n  white-space: pre-wrap;\n}\nsection {\n  margin-top: 30px;\n  padding-bottom: 10px;\n  border-bottom: 2px solid\n}\n.note {\n  color:\n  margin-top: 4px;\n  font-size: 0.9em;\n}\n</style>\n</head>\n<body>\n<h1>Font Preview</h1>\n<p class="note">Automatically generated preview for all fonts</p>\n'
HTML_END = "</body></html>"


def find_fonts(root="."):
    font_files = []
    for dirpath, _, filenames in os.walk(root):
        font_files.extend((os.path.join(dirpath, file) for file in filenames if file.lower().endswith(FONT_EXTENSIONS)))
    return sorted(font_files)


def create_font_face(font_path, font_id):
    rel_path = os.path.relpath(font_path).replace("\\", "/")
    return f"@font-face {{\n  font-family: 'f_{font_id}';\n  src: url('{html.escape(rel_path)}');\n}}"


def generate_preview(fonts):
    styles = ""
    sections = ""
    for i, font_path in enumerate(fonts, 1):
        font_id = f"font{i}"
        font_name = Path(font_path).name
        styles += create_font_face(font_path, font_id) + "\n"
        escaped_sample = html.escape(SAMPLE_TEXT)
        sections += f"""\n<section>\n  <h1>{html.escape(font_name)}</h1>\n  <textarea style="font-family: 'f_{font_id}', sans-serif;">{escaped_sample}</textarea>\n  <p class="note">{html.escape(font_path)}</p>\n</section>\n"""
    return HTML_START.replace("</style>", styles + "\n</style>") + sections + HTML_END


def main():
    fonts = find_fonts(".")
    if not fonts:
        print("No font files found.")
        return
    html_content = generate_preview(fonts)
    Path(OUTPUT_FILE).write_text(html_content, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE} with {len(fonts)} font previews.")


if __name__ == "__main__":
    main()
