#!/data/data/com.termux/files/usr/bin/python

from pathlib import Path
from bs4 import BeautifulSoup
from loguru import logger


def find_html_files(cwd: str = ".") -> list[Path]:
    root_path = Path(cwd).resolve()
    html_files = [file_path for file_path in root_path.rglob("*.html") if file_path.name != "template.html"]
    for file_path in root_path.rglob("*.htm"):
        html_files.append(file_path)
    return sorted(html_files)


def extract_common_structure(html_files: list[Path]) -> dict:
    body_classes = []
    meta_tags = []
    link_tags = []
    script_tags = []
    for file_path in html_files:
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                if soup.head:
                    meta_tags.extend((str(meta) for meta in soup.head.find_all("meta")))
                    link_tags.extend((str(link) for link in soup.head.find_all("link")))
                    script_tags.extend((str(script) for script in soup.head.find_all("script") if script.get("src")))
                if soup.body and soup.body.get("class"):
                    body_classes.extend(soup.body.get("class"))
        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
    common_meta = list(set(meta_tags))
    common_links = list(set(link_tags))
    common_scripts = list(set(script_tags))
    common_body_class = " ".join(set(body_classes)) if body_classes else ""
    return {
        "meta_tags": common_meta,
        "link_tags": common_links,
        "script_tags": common_scripts,
        "body_class": common_body_class,
    }


def merge_html_content(html_files: list[Path]) -> str:
    merged_sections = []
    for file_path in html_files:
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                content = soup.body.decode_contents() if soup.body else str(soup)
                section_html = f'\n    <!-- Content from: {file_path.relative_to(Path.cwd())} -->\n    <section class="merged-content" data-source="{file_path.name}">\n        {content}\n    </section>\n'
                merged_sections.append(section_html)
        except Exception as e:
            print(f"⚠️  Error merging {file_path}: {e}")
    return "\n".join(merged_sections)


def create_template_html(
    html_files: list[Path], output_file: str = "template.html", title: str = "Merged HTML Template"
) -> bool:
    if not html_files:
        print("⚠️  No HTML files found")
        return False
    print(f"📄 Processing {len(html_files)} HTML files...")
    structure = extract_common_structure(html_files)
    merged_content = merge_html_content(html_files)
    template = f"""<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>{title}</title>\n    <!-- Common Meta Tags -->\n    {chr(10).join(("    " + tag for tag in structure["meta_tags"]))}\n    <!-- Common Stylesheets -->\n    {chr(10).join(("    " + tag for tag in structure["link_tags"]))}\n    <!-- Template Styles -->\n    <style>\n        body {{\n            font-family: Arial, sans-serif;\n            line-height: 1.6;\n            margin: 0;\n            padding: 20px;\n            background-color:\n        }}\n        .container {{\n            max-width: 1200px;\n            margin: 0 auto;\n            background: white;\n            padding: 20px;\n            box-shadow: 0 0 10px rgba(0,0,0,0.1);\n        }}\n        .merged-content {{\n            margin-bottom: 40px;\n            padding: 20px;\n            border-left: 4px solid\n            background:\n        }}\n        .merged-content::before {{\n            content: attr(data-source);\n            display: block;\n            font-weight: bold;\n            color:\n            margin-bottom: 10px;\n            font-size: 0.9em;\n        }}\n        h1, h2, h3 {{\n            color:\n        }}\n        .toc {{\n            background:\n            padding: 20px;\n            margin-bottom: 30px;\n            border-radius: 5px;\n        }}\n        .toc h2 {{\n            margin-top: 0;\n        }}\n        .toc ul {{\n            list-style: none;\n            padding-left: 0;\n        }}\n        .toc li {{\n            margin: 5px 0;\n        }}\n        .toc a {{\n            color:\n            text-decoration: none;\n        }}\n        .toc a:hover {{\n            text-decoration: underline;\n        }}\n    </style>\n    <!-- Common Scripts -->\n    {chr(10).join(("    " + tag for tag in structure["script_tags"]))}\n</head>\n<body{(' class="' + structure["body_class"] + '"' if structure["body_class"] else "")}>\n    <div class="container">\n        <h1>{title}</h1>\n        <!-- Table of Contents -->\n        <div class="toc">\n            <h2>📑 Table of Contents</h2>\n            <ul>\n{chr(10).join((f'                <li><a href="#{Path(f).stem}">{Path(f).relative_to(Path.cwd())}</a></li>' for f in html_files))}\n            </ul>\n        </div>\n        <!-- Merged Content -->\n{merged_content}\n    </div>\n    <!-- Template Scripts -->\n    <script>\n        // Add smooth scrolling\n        document.querySelectorAll('.toc a').forEach(anchor => {{\n            anchor.addEventListener('click', function (e) {{\n                e.preventDefault();\n                const target = document.querySelector(this.getAttribute('href'));\n                if (target) {{\n                    target.scrollIntoView({{ behavior: 'smooth' }});\n                }}\n            }});\n        }});\n        // Add IDs to sections for navigation\n        document.querySelectorAll('.merged-content').forEach((section, index) => {{\n            const source = section.getAttribute('data-source');\n            const id = source.replace(/\\.html?$/, '');\n            section.id = id;\n        }});\n    </script>\n</body>\n</html>\n"""
    try:
        Path(output_file).write_text(template, encoding="utf-8")
        print(f"✅ Template created successfully: {output_file}")
        print(f"📊 Merged {len(html_files)} HTML files")
        return True
    except Exception as e:
        print(f"❌ Error writing template: {e}")
        return False


def main():
    print("🔍 Searching for HTML files in current directory...")
    html_files = find_html_files()
    if not html_files:
        print("❌ No HTML files found in current directory")
        return
    print(f"📁 Found {len(html_files)} HTML files:")
    for file_path in html_files[:10]:
        print(f"   - {file_path.relative_to(Path.cwd())}")
    if len(html_files) > 10:
        print(f"   ... and {len(html_files) - 10} more")
    success = create_template_html(html_files, output_file="template.html", title="Merged HTML Template")
    if success:
        print("\n" + "=" * 60)
        print("✨ Template generation complete!")
        print("📄 Output file: template.html")
        print("=" * 60)


if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("📦 Installing BeautifulSoup4...")
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
        from bs4 import BeautifulSoup
    main()
