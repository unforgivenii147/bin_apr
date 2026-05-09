#!/data/data/com.termux/files/usr/bin/python
import re

from weasyprint import CSS, HTML

# --------------------------------------------------------
# CONFIG
# --------------------------------------------------------
INPUT_FILE = "dictionary.txt"
OUTPUT_FILE = "dictionary.pdf"
CUSTOM_FONT = "custom.ttf"


# --------------------------------------------------------
# Helper: Convert dictionary line to valid HTML
# --------------------------------------------------------
def convert_entry_to_html(raw_line):
    # The raw line starts with a word, then a tab, then markup content.
    # Example:
    # abase<TAB><C><F>...</F></C>
    try:
        word, html_body = raw_line.strip().split("\t", 1)
    except ValueError:
        # Lines without tab
        return None
    # Convert XML-like tags to HTML (basic replacements)
    html_body = html_body.replace("<br />", "<br>")
    # Some tags like <C><F><I><N> are unknown, so keep them but close them
    # OR remove them; WeasyPrint can choke on unknown tags without closing.
    # Easiest approach: strip known wrapper tags but keep their content.
    html_body = re.sub(r"</?[CFINEË]+[^>]*>", "", html_body)
    # Convert <x K="#000001">something</x> into span
    html_body = re.sub(r"<x [^>]*>", "<span>", html_body)
    html_body = html_body.replace("</x>", "</span>")
    # Convert M="dict://res/point2.png" images to something visible or remove
    # If you have actual images, convert them to real paths.
    html_body = re.sub(r'<Ë M="[^"]+" ?/?>', "", html_body)
    # Build final page HTML
    html = f"""
    <html>
    <body>
        <div class="entry">
            <h1 class="word">{word}</h1>
            <div class="definition">{html_body}</div>
        </div>
    </body>
    </html>
    """
    return html


# --------------------------------------------------------
# Build one PDF with multiple pages
# --------------------------------------------------------
def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    pages = []
    for line in lines:
        html = convert_entry_to_html(line)
        if html:
            pages.append(html)
    # Build final combined HTML (WeasyPrint automatically page-breaks)
    full_html = (
        """
    <html>
        <head>
            <style>
                @font-face {
                    font-family: "CustomFont";
                    src: url('%s');
                }
                body {
                    font-family: "CustomFont", sans-serif;
                    font-size: 16px;
                }
                .entry {
                    page-break-after: always;
                    padding: 30px;
                }
                .word {
                    margin-top: 0;
                    color: #222;
                }
                .definition {
                    margin-top: 10px;
                    line-height: 1.5;
                }
            </style>
        </head>
        <body>
    """
        % CUSTOM_FONT
    )
    for p in pages:
        full_html += p
    full_html += "</body></html>"
    HTML(string=full_html).write_pdf(OUTPUT_FILE)
    print("PDF created:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
