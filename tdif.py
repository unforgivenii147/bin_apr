#!/data/data/com.termux/files/usr/bin/python

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

import argparse
import difflib
import sys
from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Footer, Header, Label, Static


class DiffLine(Static):
    def __init__(self, text: str, line_type: str, line_num: int | None = None) -> None:
        self.raw_text = text
        self.line_type = line_type
        self.line_num = line_num
        display_text = self._create_display_text()
        super().__init__(display_text)
        self._apply_styling()

    def _create_display_text(self) -> str:
        prefix = f"{self.line_num:4d}" if self.line_num is not None else "    "
        safe_text = self.raw_text.replace("[", "[]")
        if self.line_type == " ":
            return f"{prefix}  {safe_text}"
        if self.line_type == "-":
            return f"{prefix} - {safe_text}"
        if self.line_type == "+":
            return f"{prefix} + {safe_text}"
        if self.line_type == "?":
            return f"{prefix} ? {safe_text}"
        return f"{prefix}   {safe_text}"

    def _apply_styling(self):
        if self.line_type == " ":
            self.styles.background = Color(30, 30, 30)
            self.styles.color = Color(200, 200, 200)
        elif self.line_type == "-":
            self.styles.background = Color(80, 30, 30)
            self.styles.color = Color(255, 150, 150)
        elif self.line_type == "+":
            self.styles.background = Color(30, 80, 30)
            self.styles.color = Color(150, 255, 150)
        elif self.line_type == "?":
            self.styles.background = Color(60, 60, 30)
            self.styles.color = Color(255, 255, 150)


class DiffPanel(ScrollableContainer):
    def __init__(self, title: str, lines: list[tuple[str, str, int]]) -> None:
        super().__init__()
        self.panel_title = title
        self.lines = lines

    def compose(self) -> ComposeResult:
        yield Label(f"[bold]{self.panel_title}[/bold]", classes="panel-title")
        for text, line_type, line_num in self.lines:
            yield DiffLine(text, line_type, line_num)

    def on_mount(self) -> None:
        self.can_focus = True
        self.can_focus_children = True


class DiffViewerApp(App):
    CSS = "\n    Screen {\n        background: $surface;\n    }\n    .panel-title {\n        padding: 1;\n        text-align: center;\n        background: $primary;\n        color: $text;\n        text-style: bold;\n        width: 100%;\n    }\n    DiffPanel {\n        border: solid $primary;\n        height: 100%;\n        width: 50%;\n        overflow-y: auto;\n    }\n    DiffPanel:focus {\n        border: double $secondary;\n    }\n    DiffLine {\n        padding: 0 1;\n        width: 100%;\n        height: 1;\n    }\n    Horizontal {\n        height: 1fr;\n    }\n    Header {\n        background: $primary-lighten-1;\n    }\n    Footer {\n        background: $primary-darken-1;\n    }\n    "
    BINDINGS: ClassVar = [
        ("q", "quit", "Quit"),
        ("f1", "toggle_panel", "Focus Next Panel"),
        ("ctrl+c", "quit", "Quit"),
        ("/", "search", "Search"),
        ("n", "next_search", "Next Result"),
    ]

    def __init__(self, file1: str, file2: str) -> None:
        super().__init__()
        self.file1 = Path(file1)
        self.file2 = Path(file2)
        self.left_lines = []
        self.right_lines = []
        self.search_term = ""
        self.search_results = []

    def read_file(self, filepath: Path) -> list[str]:
        try:
            with Path(filepath).open(encoding="utf-8") as f:
                return f.readlines()
        except UnicodeDecodeError:
            try:
                with Path(filepath).open(encoding="latin-1") as f:
                    return f.readlines()
            except Exception as e:
                self.notify(f"Error reading {filepath}: {e}", severity="error")
                return []
        except Exception as e:
            self.notify(f"Error reading {filepath}: {e}", severity="error")
            return []

    def compute_diff(self) -> None:
        lines1 = self.read_file(self.file1)
        lines2 = self.read_file(self.file2)
        lines1 = [line.rstrip("\n") for line in lines1]
        lines2 = [line.rstrip("\n") for line in lines2]
        differ = difflib.Differ()
        diff = list(differ.compare(lines1, lines2))
        left_line_num = 0
        right_line_num = 0
        for line in diff:
            line_type = line[0] if line else " "
            content = line[2:] if len(line) > 2 else ""
            if line_type == " ":
                left_line_num += 1
                right_line_num += 1
                self.left_lines.append((content, line_type, left_line_num))
                self.right_lines.append((content, line_type, right_line_num))
            elif line_type == "-":
                left_line_num += 1
                self.left_lines.append((content, line_type, left_line_num))
                self.right_lines.append(("", " ", None))
            elif line_type == "+":
                right_line_num += 1
                self.left_lines.append(("", " ", None))
                self.right_lines.append((content, line_type, right_line_num))
            elif line_type == "?":
                self.left_lines.append((content, line_type, None))
                self.right_lines.append((content, line_type, None))

    def compose(self) -> ComposeResult:
        yield Header()
        self.compute_diff()
        with Horizontal():
            left_panel = DiffPanel(str(self.file1), self.left_lines)
            right_panel = DiffPanel(str(self.file2), self.right_lines)
            yield left_panel
            yield right_panel
        yield Footer()

    def on_mount(self) -> None:
        panels = self.query(DiffPanel)
        if panels:
            panels.first().focus()

    def action_toggle_panel(self) -> None:
        current = self.focused
        if current and isinstance(current, DiffPanel):
            panels = list(self.query(DiffPanel))
            for i, panel in enumerate(panels):
                if panel == current:
                    next_panel = panels[(i + 1) % len(panels)]
                    next_panel.focus()
                    break
        else:
            panels = self.query(DiffPanel)
            if panels:
                panels.first().focus()

    def action_search(self) -> None:

        def on_input(submitted_text: str) -> None:
            if submitted_text:
                self.search_term = submitted_text
                self.highlight_search_results()

        self.push_screen("input", on_input, title="Search", instructions="Enter text to search for:")

    def highlight_search_results(self) -> None:
        if not self.search_term:
            return
        for line in self.query(DiffLine):
            line.styles.background = None
        for line in self.query(DiffLine):
            if self.search_term.lower() in line.raw_text.lower():
                line.styles.background = Color(70, 70, 150)

    def action_next_search(self) -> None:
        self.notify("Next search result (feature not fully implemented)")


def main():
    parser = argparse.ArgumentParser(
        description="Compare two files and show their differences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\nExamples:\n  %(prog)s file1.txt file2.txt\n  %(prog)s --help\n        ",
    )
    parser.add_argument("file1", help="First file to compare")
    parser.add_argument("file2", help="Second file to compare")
    args = parser.parse_args()
    file1 = Path(args.file1)
    file2 = Path(args.file2)
    if not file1.exists():
        print(f"Error: File '{file1}' does not exist")
        return 1
    if not file2.exists():
        print(f"Error: File '{file2}' does not exist")
        return 1
    app = DiffViewerApp(str(file1), str(file2))
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
