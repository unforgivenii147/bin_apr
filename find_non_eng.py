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
import os
import sys
from collections import Counter
from pathlib import Path

import pycld2
from dh import is_binary


class LanguageDetector:
    def __init__(self, min_bytes=100, max_bytes=10000) -> None:
        self.min_bytes = min_bytes
        self.max_bytes = max_bytes
        self.stats = {
            "total_files": 0,
            "skipped_binary": 0,
            "skipped_small": 0,
            "skipped_error": 0,
            "non_english": [],
            "languages": Counter(),
        }

    def is_text_file(self, filepath):
        return not is_binary(filepath)

    def detect_language(self, filepath):
        try:
            with Path(filepath).open(encoding="utf-8", errors="ignore") as f:
                content = f.read(self.max_bytes)
            if len(content) < self.min_bytes:
                return (False, "TOO_SHORT", None, None)
            is_reliable, _, details = pycld2.detect(content)
            if details and len(details) > 0:
                lang_name, lang_code, percent, _ = details[0]
                return (is_reliable, lang_name, lang_code, percent)
            return (False, "UNKNOWN", None, None)
        except pycld2.error as e:
            return (False, f"CLD2_ERROR: {e}", None, None)
        except Exception as e:
            return (False, f"ERROR: {e}", None, None)

    def scan_directory(self, directory, show_progress=True, only_report_non_english=True):
        directory = Path(directory)
        if not directory.exists():
            print(f"Error: Directory '{directory}' does not exist")
            return
        print(f"🔍 Scanning directory: {directory.absolute()}")
        print("=" * 60)
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                filepath = root_path / file
                if file.startswith("."):
                    continue
                self.stats["total_files"] += 1
                if show_progress:
                    print(f"\n{filepath} [Files: {self.stats['total_files']}]", end="", flush=True)
                if not self.is_text_file(filepath):
                    self.stats["skipped_binary"] += 1
                    continue
                is_reliable, lang_name, lang_code, percent = self.detect_language(filepath)
                if lang_name in {"TOO_SHORT", "UNKNOWN", None} or lang_name.startswith(("ERROR:", "CLD2_ERROR:")):
                    self.stats["skipped_small" if lang_name == "TOO_SHORT" else "skipped_error"] += 1
                    continue
                self.stats["languages"][lang_name] += 1
                if lang_code != "en" or not only_report_non_english:
                    if lang_code == "en" and (not is_reliable) and only_report_non_english or lang_code != "en":
                        self.stats["non_english"].append(
                            {
                                "file": filepath,
                                "language": lang_name,
                                "code": lang_code,
                                "reliable": is_reliable,
                                "confidence": percent,
                            }
                        )
        print("\n" + "=" * 60)
        self.report_results(only_report_non_english)

    def report_results(self, only_report_non_english=True):
        print("\n📊 SCAN RESULTS")
        print("=" * 60)
        print(f"📁 Total files processed: {self.stats['total_files']}")
        print(f"⏭️  Skipped binary files: {self.stats['skipped_binary']}")
        print(f"📏 Skipped small files (<100 bytes): {self.stats['skipped_small']}")
        print(f"❌ Skipped (errors): {self.stats['skipped_error']}")
        if only_report_non_english:
            print(f"🌍 Non-English files found: {len(self.stats['non_english'])}")
        else:
            print(f"🌍 Total text files analyzed: {sum(self.stats['languages'].values())}")
        if self.stats["languages"]:
            print("\n📈 Language Distribution:")
            for lang, count in self.stats["languages"].most_common():
                print(f"  • {lang}: {count} files")
        if self.stats["non_english"]:
            print(f"\n📝 Non-English Files ({len(self.stats['non_english'])}):")
            print("-" * 60)
            non_english_by_lang = {}
            for item in self.stats["non_english"]:
                lang = item["language"]
                if lang not in non_english_by_lang:
                    non_english_by_lang[lang] = []
                non_english_by_lang[lang].append(item)
            for lang, files in sorted(non_english_by_lang.items()):
                print(f"\n  [{lang}] - {len(files)} files:")
                for item in files[:10]:
                    reliability = "✓" if item["reliable"] else "?"
                    confidence = item["confidence"] or 0
                    rel_str = f"[{reliability} {confidence}%]" if confidence else "[?]"
                    print(f"    {rel_str} {item['file']}")
                if len(files) > 10:
                    print(f"    ... and {len(files) - 10} more")
        else:
            print("\n✅ No non-English files found!")


def main():
    parser = argparse.ArgumentParser(description="Recursively find non-English files using pycld2")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan (default: current directory)")
    parser.add_argument(
        "--min-bytes", type=int, default=100, help="Minimum bytes to read for language detection (default: 100)"
    )
    parser.add_argument(
        "--max-bytes", type=int, default=10000, help="Maximum bytes to read from each file (default: 10000)"
    )
    parser.add_argument("--all", "-a", action="store_true", help="Report all files, including English ones")
    parser.add_argument("--no-progress", "-np", action="store_true", help="Don't show progress")
    parser.add_argument("--output", "-o", type=str, help="Output results to file")
    args = parser.parse_args()
    detector = LanguageDetector(min_bytes=args.min_bytes, max_bytes=args.max_bytes)
    detector.scan_directory(args.directory, show_progress=not args.no_progress, only_report_non_english=not args.all)
    if args.output:
        from contextlib import redirect_stdout

        with Path(args.output).open("w", encoding="utf-8") as f, redirect_stdout(f):
            detector.report_results(only_report_non_english=not args.all)
        print(f"\n✅ Results saved to: {args.output}")


if __name__ == "__main__":
    try:
        import pycld2
    except ImportError:
        print("Error: pycld2 is not installed. Install it with:")
        print("  pip install pycld2")
        print("\nOn Termux, you might need:")
        print("  pkg install clang")
        print("  pip install pycld2")
        sys.exit(1)
    main()
