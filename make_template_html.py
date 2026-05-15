    DIRECTORY,
    CHUNK_SIZE,
    non_english_pattern,
    split_into_chunks,
    EXCLUDE_DIRS,
    read_file,
    extract_words,
    START_DIR,
    NUM_PROCESSES,
    main,
    random_key,
    decrypt_file,
    fetch_content_length,
    fsz,
    MAX_QUEUE,
    parse_minutes,
    get_all_files,
    compute_hashes,
    group_similar_files,
    EXCLUDE_DIRS,
    DICT_FILE,
    load_dictionary,
    setup_readline,
    translate,
    prefix_search,
    fuzzy_search,
    interactive_mode,
    OUTPUT_DIR,
    ARCHIVE_EXTENSIONS,
    get_unique_filepath,
    extract_entities_from_content,
    is_python_file_no_extension,
    process_single_file,
    process_archive,
    worker_process,
    get_current_folder_name,
    folder_exists_in_db,
    get_imports_from_file,
    copy_groups,
    write_report,
    colorize_score,
    write_matrix,
    main,
    safe_mkdir,
    cwd,
    process_file,
    collect_files_by_extension,
    main,
    OUTPUT_DIR,
    ALLOWED_PYTHON_EXTENSIONS,
    MAX_CHARS,
    clean_file,
    get_mode,
    SIZE_THRESHOLD,
    OLD_PRINT_RE,
    _open_source,
    _read_text,
    _has_rich_print_import,
    regex_flag,
    tokenizer_confirm,
    fsz,
    gsz,
    logger,
    count_lines_of_code,
    scan_directory,
    save_file,
    find_chunk_boundary,
    chunk_text,
    translate_file,
    is_english,
    find_site_packages,
    list_installed_packages,
    get_wheel_tags,
    copy_package_files,
    copy_dist_info,
    copy_scripts,
    build_wheel,
    repack,
    ERROR_DIR,
    OK_DIR,
    ensure_dirs,
    unique_destination,
    get_installed_debian_packages,
    save_packages,
    main,
    translate_chunk,
    translate_file,
    chunk_text,
    write_text_file,
    build_output_path,
    SUPPORTED_FORMATS,
    is_text_file,
    INPUT_FILE,
    OUTPUT_FILE,
    translate_word,
    main,
    EXCLUDE_PREFIXES,
    parser,
    EXCLUDE_DIRS,
    ALLOWED_EXT,
    CHUNK_SIZE,
    LOG_EXT,
    PATTERNS,
    ValidationError,
    PY_LANGUAGE,
    parser,
    should_preserve_comment,
    find_docstring_ranges,
    py_version,
    TIMESTAMP_RE,
    to_ms,
    from_ms,
    THRESHOLD,
    video,
    txtfile,
    OUT_DIR,
    extract_file,
    folder_imports,
    get_dir_size,
    extract_zst_file,
    find_archives,
    VALID,
    get_node_text,
    get_relative_path,
    processed_files_count,
    folders_found,
    total_definitions,
    BASE_DIR,
    N_JOBS,
    compress_chunk,
    _executor,
    get_dirs,
    main,
    OUT_PREFIX,
    CHUNK_SIZE,
    QUERY_STRING,
    should_preserve_comment,
    MAX_WORKERS,
    find_html_files,
    OUTPUT_DIR,
    ASSETS_DIR,
    TIMEOUT,
    MAX_WORKERS,
    get_all_dist_info_dirs,
    EXCLUDE_PREFIXES,
    get_sha256,
    find_png_files,
    ts_remover,
    EXCLUDED,
    read_requirements,
    safe_rename,
    unique_path,
    EXCLUDED_DIRS,
    format_time,
    ANSI_RESET,
    main,
    fsz,
    is_git_repo,
    gather_python_files,
    worker,
    find_dist_info_dir,
    UNPACKED_WHEELS_SOURCE_DIR,
    WHEELS_OUTPUT_DIR,
    find_dist_info_dir,
    env_vars,
    env_var_pattern,
    output_filename,
    OUTPUT_FILE,
    sha256_text,
    is_const_name,
    FONT_EXTENSIONS,
    FONT_SIZES,
    find_fonts,
    main,
    setup_logging,
    MAX_WORKERS,
    main,
    INPUT_FILE,
    main,
    can_fetch,
)
#!/data/data/com.termux/files/usr/bin/python

from pathlib import Path

from bs4 import BeautifulSoup


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
    html_files = find_html_files()
    success = create_template_html(html_files, output_file="template.html", title="Merged HTML Template")
    if success:
        print("Output file: template.html")


if __name__ == "__main__":
    main()
