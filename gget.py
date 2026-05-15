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

import hashlib
import json
import signal
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote

import requests
from rich.console import Console
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn

console = Console()
CHUNK_SIZE = 1024 * 1024 * 5
MAX_WORKERS = 4
STATE_SUFFIX = ".progress"


class Downloader:
    def __init__(self, url, output_path=None, expected_hash=None) -> None:
        self.url = url
        self.stop_event = threading.Event()
        self.file_size = 0
        self.filename = output_path
        self.expected_hash = expected_hash
        self.state_file = None
        self.progress_data = {"downloaded_chunks": [], "total_chunks": 0}
        self.lock = threading.Lock()

    def _get_info(self):
        resp = requests.head(self.url, allow_redirects=True, timeout=10)
        resp.raise_for_status()
        self.file_size = int(resp.headers.get("content-length", 0))
        if not self.filename:
            cd = resp.headers.get("Content-Disposition")
            if cd and "filename=" in cd:
                self.filename = cd.split("filename=")[1].strip(' "')
            else:
                self.filename = unquote(self.url.split("/")[-1]) or "downloaded_file"
        self.state_file = Path(f"{self.filename}{STATE_SUFFIX}")

    def _verify_integrity(self):
        sha256_hash = hashlib.sha256()
        console.print("\n[bold cyan]Verifying file integrity...[/]")
        with Path(self.filename).open("rb") as f:
            for byte_block in iter(lambda: f.read(1024 * 1024), b""):
                sha256_hash.update(byte_block)
        calculated_hash = sha256_hash.hexdigest()
        if self.expected_hash:
            if calculated_hash.lower() == self.expected_hash.lower():
                console.print("[bold green]✅ Integrity Verified: Hashes match![/]")
            else:
                console.print("[bold red]❌ Integrity Check Failed![/]")
                console.print(f"Expected: {self.expected_hash}")
                console.print(f"Got:      {calculated_hash}")
        else:
            console.print(f"[bold yellow]SHA-256 Checksum:[/] {calculated_hash}")
            console.print("[italic]Provide this hash next time to verify automatically.[/]")

    def _load_state(self):
        if self.state_file.exists():
            try:
                with Path(self.state_file).open(encoding="utf-8") as f:
                    self.progress_data = json.load(f)
            except Exception:
                pass

    def _save_state(self):
        with self.lock, Path(self.state_file).open("w", encoding="utf-8") as f:
            json.dump(self.progress_data, f)

    def _download_chunk(self, chunk_id, start, end, progress, task_id):
        if self.stop_event.is_set():
            return
        headers = {"Range": f"bytes={start}-{end}"}
        try:
            with requests.get(self.url, headers=headers, stream=True, timeout=15) as r:
                r.raise_for_status()
                with Path(self.filename).open("r+b") as f:
                    f.seek(start)
                    for data in r.iter_content(chunk_size=1024 * 64):
                        if self.stop_event.is_set():
                            return
                        f.write(data)
                        progress.update(task_id, advance=len(data))
            with self.lock:
                self.progress_data["downloaded_chunks"].append(chunk_id)
            self._save_state()
        except Exception:
            pass

    def start(self):
        self._get_info()
        self._load_state()
        if not Path(self.filename).exists():
            with Path(self.filename).open("wb") as f:
                f.truncate(self.file_size)
        chunks = [(i, min(i + CHUNK_SIZE - 1, self.file_size - 1)) for i in range(0, self.file_size, CHUNK_SIZE)]
        self.progress_data["total_chunks"] = len(chunks)
        pending_chunks = [
            (idx, s, e) for idx, (s, e) in enumerate(chunks) if idx not in self.progress_data["downloaded_chunks"]
        ]
        if not pending_chunks:
            console.print(f"[bold green]✔ {self.filename} is already finished![/]")
            self._verify_integrity()
            return
        with Progress(
            TextColumn("[bold blue]{task.fields[filename]}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            main_task = progress.add_task(
                "download",
                filename=self.filename,
                total=self.file_size,
                completed=len(self.progress_data["downloaded_chunks"]) * CHUNK_SIZE,
            )
            signal.signal(signal.SIGINT, lambda s, f: self.stop_event.set())
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [
                    executor.submit(self._download_chunk, cid, s, e, progress, main_task)
                    for cid, s, e in pending_chunks
                ]
                for f in futures:
                    if self.stop_event.is_set():
                        break
                    f.result()
        if not self.stop_event.is_set():
            self.state_file.unlink(missing_ok=True)
            console.print(f"\n[bold green]Download Complete: {self.filename}[/]")
            self._verify_integrity()
        else:
            console.print("\n[bold yellow]Download Paused. Run again to resume.[/]")
            sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/] python downloader.py <URL> [output_name] [expected_sha256]")
        sys.exit(1)
    url_arg = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None
    hash_arg = sys.argv[3] if len(sys.argv) > 3 else None
    dl = Downloader(url_arg, out_arg, hash_arg)
    dl.start()
