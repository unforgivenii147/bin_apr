#!/data/data/com.termux/files/usr/bin/python
import html
import os
from pathlib import Path
from loguru import logger

FONT_EXTENSIONS = (".ttf", ".otf", ".woff", ".woff2", ".eot")
SAMPLE_TEXT = "Lorem ipsum dolor sit amet\nهنر برتر از گوهر آمد پدید"
OUTPUT_FILE = "fontpreview.html"
HTML_START = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Font Preview</title>
<style>
body {
  background: #fafafa;
  color: #222;
  font-family: system-ui, sans-serif;
  margin: 0 auto;
  padding: 20px;
  max-width: 960px;
}
h1 {
  margin-top: 40px;
  font-size: 1.6em;
  border-bottom: 1px solid #ddd;
  padding-bottom: .3em;
  color: #333;
}
textarea {
  width: 100%;
  height: 100px;
  padding: 12px;
  margin-top: 6px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 1.1em;
  box-sizing: border-box;
  resize: vertical;
  white-space: pre-wrap;
}
section {
  margin-top: 30px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}
.note {
  color: #666;
  margin-top: 4px;
  font-size: 0.9em;
}
</style>
</head>
<body>
<h1>Font Preview</h1>
<p class="note">Automatically generated preview for all fonts</p>
"""
HTML_END = """</body></html>"""


def find_fonts(root="."):
    font_files = []
    for dirpath, _, filenames in os.walk(root):
        font_files.extend(os.path.join(dirpath, file) for file in filenames if file.lower().endswith(FONT_EXTENSIONS))
    return sorted(font_files)


def create_font_face(font_path, font_id):
    rel_path = os.path.relpath(font_path).replace("\\", "/")
    return f"""@font-face {{
  font-family: 'f_{font_id}';
  src: url('{html.escape(rel_path)}');
}}"""


def generate_preview(fonts):
    styles = ""
    sections = ""
    for i, font_path in enumerate(fonts, 1):
        font_id = f"font{i}"
        font_name = Path(font_path).name
        styles += create_font_face(font_path, font_id) + "\n"
        escaped_sample = html.escape(SAMPLE_TEXT)
        sections += f"""
<section>
  <h1>{html.escape(font_name)}</h1>
  <textarea style="font-family: 'f_{font_id}', sans-serif;">{escaped_sample}</textarea>
  <p class="note">{html.escape(font_path)}</p>
</section>
"""
    return HTML_START.replace("</style>", styles + "\n</style>") + sections + HTML_END


def main():
    fonts = find_fonts(".")
    if not fonts:
        logger.info("No font files found.")
        return
    html_content = generate_preview(fonts)
    Path(OUTPUT_FILE).write_text(html_content, encoding="utf-8")
    logger.info(f"Generated {OUTPUT_FILE} with {len(fonts)} font previews.")


if __name__ == "__main__":
    main()
