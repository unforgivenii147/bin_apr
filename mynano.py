#!/data/data/com.termux/files/usr/bin/python3
from utils import (
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

import readline
import rlcompleter
import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.log import TextLog
from textual.widgets import Footer, Header, TextEditor


class BasicEditor(App):
    BINDINGS = [("o", "open_file", "Open"), ("s", "save_file", "Save"), ("q", "app_quit", "Quit")]

    def __init__(self, filename: str | None = None):
        super().__init__()
        self.filename = filename
        self.is_dirty = False

    def setup_readline(self):
        readline.parse_and_bind("tab: complete")
        readline.set_completer(rlcompleter.Completer(namespace=sys.modules).complete)

    def compose(self) -> ComposeResult:
        self.setup_readline()
        yield Header()
        with Container():
            yield TextEditor(id="editor", name="editor")
            yield TextLog(id="log", height=2, panel=True, label="Status")
        yield Footer()

    def on_mount(self) -> None:
        editor = self.query_one(TextEditor)
        log = self.query_one(TextLog)
        if self.filename:
            try:
                with Path(self.filename).open("r", encoding="utf-8") as f:
                    editor.text = f.read()
                self.title = f"Basic Editor - {self.filename}"
                log.write(f"Opened file: {self.filename}")
            except FileNotFoundError:
                log.write(f"Error: File '{self.filename}' not found.")
                self.title = "Basic Editor - New File"
            except Exception as e:
                log.write(f"Error opening file: {e}")
                self.title = "Basic Editor - New File"
        else:
            self.title = "Basic Editor - New File"
            log.write("New file. Use Ctrl+O to open or Ctrl+S to save.")

    def action_open_file(self) -> None:
        log = self.query_one(TextLog)
        editor = self.query_one(TextEditor)
        try:
            filename = input("Enter filename to open: ")
            if filename:
                self.filename = filename
                with Path(self.filename).open("r", encoding="utf-8") as f:
                    editor.text = f.read()
                self.title = f"Basic Editor - {self.filename}"
                log.write(f"Opened file: {self.filename}")
                self.is_dirty = False
            else:
                log.write("Open cancelled.")
        except FileNotFoundError:
            log.write(f"Error: File '{self.filename}' not found.")
        except Exception as e:
            log.write(f"Error opening file: {e}")

    def action_save_file(self) -> None:
        log = self.query_one(TextLog)
        editor = self.query_one(TextEditor)
        if not self.filename:
            try:
                filename = input("Enter filename to save as: ")
                if filename:
                    self.filename = filename
                else:
                    log.write("Save cancelled.")
                    return
            except Exception as e:
                log.write(f"Error getting filename: {e}")
                return
        try:
            Path(self.filename).write_text(editor.text, encoding="utf-8")
            self.title = f"Basic Editor - {self.filename}"
            log.write(f"Saved file: {self.filename}")
            self.is_dirty = False
        except Exception as e:
            log.write(f"Error saving file: {e}")

    def action_app_quit(self) -> None:
        log = self.query_one(TextLog)
        editor = self.query_one(TextEditor)
        if editor.text and self.is_dirty:
            try:
                confirm = input("You have unsaved changes. Are you sure you want to quit? (y/n): ")
                if confirm.lower() == "y":
                    self.exit()
                else:
                    log.write("Quit cancelled.")
            except Exception as e:
                log.write(f"Error during quit confirmation: {e}")
        else:
            self.exit()

    def on_text_editor_changed(self, event: TextEditor.Changed) -> None:
        self.is_dirty = True
        self.query_one(Footer).key_display = [
            ("o", "Open", "primary"),
            ("s", "Save", "primary"),
            ("q", "Quit", "primary"),
        ]
        if self.is_dirty:
            self.query_one(Footer).key_display.append(("Ctrl+S", "Save", "warning"))


if __name__ == "__main__":
    initial_filename = sys.argv[1] if len(sys.argv) > 1 else None
    app = BasicEditor(filename=initial_filename)
    app.run()
