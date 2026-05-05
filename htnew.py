#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path

from loguru import logger


def create_html_template(filename="index.html"):
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <!-- Your content here -->
</body>
</html>
"""
    try:
        Path(filename).write_text(html_template, encoding="utf-8")
        logger.info(f"Successfully created {filename} in {Path.cwd()}")
    except Exception as e:
        logger.info(f"Error: {e}")


if __name__ == "__main__":
    create_html_template()
