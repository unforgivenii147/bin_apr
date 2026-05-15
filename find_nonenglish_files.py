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

import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pycld2
from dh import TXT_EXT

MIN_TEXT_LENGTH = 20
SUPPORTED_EXTENSIONS = TXT_EXT
ENGLISH_LANGUAGES = {"en", "en_US", "en_GB"}
MAX_FILE_SIZE = 1024 * 1024


def detect_language(text: str) -> tuple[str | None, float]:
    if not text or len(text) < MIN_TEXT_LENGTH:
        return (None, 0)
    try:
        reliable, _, details = pycld2.detect(text)
        if reliable and details:
            primary_lang = details[0][0]
            confidence = details[0][2]
            return (primary_lang, confidence)
    except Exception:
        pass
    return (None, 0)


def is_likely_english(text: str, threshold: float = 70.0) -> bool:
    lang, confidence = detect_language(text)
    if lang is None:
        return False
    return lang in ENGLISH_LANGUAGES and confidence >= threshold


def read_file_safely(filepath: Path) -> str | None:
    try:
        return filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
            try:
                return filepath.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
    except Exception:
        pass
    return None


def get_file_sample(text: str, max_lines: int = 50, max_chars: int = 5000) -> str:
    lines = text.split("\n")[:max_lines]
    sample = "\n".join(lines)
    if len(sample) > max_chars:
        sample = sample[:max_chars]
    return sample


def analyze_directory(directory: str = ".", show_all: bool = False) -> dict:
    directory = Path(directory).resolve()
    print(f"🔍 Scanning directory: {directory}")
    print("=" * 70)
    results = {
        "total_files": 0,
        "checked_files": 0,
        "skipped_small": 0,
        "skipped_binary": 0,
        "skipped_encoding": 0,
        "non_english": defaultdict(list),
        "english": [],
        "undetermined": [],
        "language_stats": Counter(),
        "directory_stats": defaultdict(lambda: {"total": 0, "non_english": 0}),
    }
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"__pycache__", "node_modules"}]
        current_dir = Path(root)
        rel_dir = current_dir.relative_to(directory)
        for file in files:
            filepath = current_dir / file
            if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if filepath.stat().st_size > MAX_FILE_SIZE:
                results["skipped_binary"] += 1
                continue
            results["total_files"] += 1
            results["directory_stats"][str(rel_dir)]["total"] += 1
            content = read_file_safely(filepath)
            if content is None:
                results["skipped_encoding"] += 1
                continue
            sample = get_file_sample(content)
            if len(sample) < MIN_TEXT_LENGTH:
                results["skipped_small"] += 1
                continue
            lang, confidence = detect_language(sample)
            if lang is None:
                results["undetermined"].append(filepath)
                continue
            results["checked_files"] += 1
            results["language_stats"][lang] += 1
            if lang in ENGLISH_LANGUAGES and confidence >= 70:
                results["english"].append(filepath)
            else:
                results["non_english"][lang].append(filepath)
                results["directory_stats"][str(rel_dir)]["non_english"] += 1
    return results


def print_results(results: dict, show_files: bool = False):
    print("\n" + "=" * 70)
    print("📊 LANGUAGE DETECTION RESULTS")
    print("=" * 70)
    total = results["total_files"]
    checked = results["checked_files"]
    non_english_total = sum((len(files) for files in results["non_english"].values()))
    english_total = len(results["english"])
    undetermined = len(results["undetermined"])
    print(f"\n📁 Files scanned: {total}")
    print(f"   ├─ Successfully analyzed: {checked} ({checked / total * 100:.1f}%)")
    print(f"   ├─ Skipped (too small): {results['skipped_small']}")
    print(f"   ├─ Skipped (binary/large): {results['skipped_binary']}")
    print(f"   └─ Skipped (encoding issues): {results['skipped_encoding']}")
    print("\n🌍 Language breakdown:")
    print(f"   ├─ 🇺🇸 English files: {english_total}")
    for lang, files in sorted(results["non_english"].items(), key=lambda x: len(x[1]), reverse=True):
        percentage = len(files) / checked * 100 if checked > 0 else 0
        print(f"   ├─ 🌐 {lang.upper()}: {len(files)} files ({percentage:.1f}%)")
    if undetermined > 0:
        print(f"   └─ ❓ Undetermined: {undetermined}")
    if results["directory_stats"]:
        print("\n📂 Directories with most non-English files:")
        dirs_with_non_english = [
            (dir_path, stats) for dir_path, stats in results["directory_stats"].items() if stats["non_english"] > 0
        ]
        dirs_with_non_english.sort(key=lambda x: x[1]["non_english"], reverse=True)
        for dir_path, stats in dirs_with_non_english[:10]:
            percentage = stats["non_english"] / stats["total"] * 100
            print(f"   ├─ {(dir_path if dir_path != '.' else '(root)')}:")
            print(f"   │   {stats['non_english']}/{stats['total']} files ({percentage:.1f}% non-English)")
    if show_files and results["non_english"]:
        print("\n📄 Non-English files by language:")
        for lang, files in sorted(results["non_english"].items()):
            if files:
                print(f"\n   🌐 {lang.upper()} ({len(files)} files):")
                for filepath in files[:20]:
                    rel_path = filepath.relative_to(Path.cwd()) if filepath.is_absolute() else filepath
                    print(f"      └─ {rel_path}")
                if len(files) > 20:
                    print(f"      └─ ... and {len(files) - 20} more")
    print("\n" + "=" * 70)
    print("🎯 RECOMMENDATION")
    print("=" * 70)
    if non_english_total == 0:
        print("✅ All files appear to be in English! No translation needed.")
    else:
        print(f"📢 Found {non_english_total} non-English files that may need translation.")
        dirs_to_translate = [
            (dir_path, stats) for dir_path, stats in results["directory_stats"].items() if stats["non_english"] > 0
        ]
        if dirs_to_translate:
            print("\n📌 Directories to translate (by priority):")
            for dir_path, stats in sorted(dirs_to_translate, key=lambda x: x[1]["non_english"], reverse=True):
                print(f"   └─ {(dir_path if dir_path != '.' else 'current directory')}:")
                print(f"       {stats['non_english']} non-English files to translate")
    print("=" * 70)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Find non-English files in directory recursively using pycld2")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan (default: current directory)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed file listing")
    parser.add_argument(
        "-l", "--list-languages", action="store_true", help="List all detected languages and their counts"
    )
    args = parser.parse_args()
    try:
        results = analyze_directory(args.directory)
        print_results(results, show_files=args.verbose or args.list_languages)
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
