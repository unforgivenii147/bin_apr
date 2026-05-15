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
import shutil
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import ssdeep
import xxhash
from tqdm import tqdm

EXCLUDE_DIRS = {".git", "__pycache__", "node_modules"}


class FileSimilarityDetector:
    def __init__(self, cwd=".") -> None:
        self.cwd = Path(cwd)
        self.file_hashes = {}
        self.duplicates = defaultdict(list)

    def scan_files(self):
        for root, dirs, files in os.walk(self.cwd):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for name in files:
                path = Path(root) / name
                if not path.is_symlink():
                    yield path

    @staticmethod
    def hash_file(path: Path):
        try:
            data = path.read_bytes()
            return (str(path), xxhash.xxh64(data).hexdigest(), ssdeep.hash(data))
        except Exception:
            return (str(path), None, None)

    def process_files(self, files):
        files = list(files)
        print(f"Processing {len(files)} files...")
        with ThreadPoolExecutor() as pool:
            futures = [pool.submit(self.hash_file, f) for f in files]
            for fut in tqdm(as_completed(futures), total=len(futures), desc="Hashing"):
                path, xh, sh = fut.result()
                if not xh or not sh:
                    continue
                self.file_hashes[path] = {"xxhash": xh, "ssdeep": sh}
                self.duplicates[xh].append(path)
        self.duplicates = {h: paths for h, paths in self.duplicates.items() if len(paths) > 1}

    def find_similarity_groups(self, threshold: int):
        excluded = {p for group in self.duplicates.values() for p in group}
        candidates = [p for p in self.file_hashes if p not in excluded]
        visited = set()
        groups = []
        for i, p1 in enumerate(tqdm(candidates, desc="Finding Similarities")):
            if p1 in visited:
                continue
            group = [p1]
            visited.add(p1)
            h1 = self.file_hashes[p1]["ssdeep"]
            for p2 in candidates[i + 1 :]:
                if p2 in visited:
                    continue
                if ssdeep.compare(h1, self.file_hashes[p2]["ssdeep"]) >= threshold:
                    group.append(p2)
                    visited.add(p2)
            if len(group) > 1:
                groups.append(group)
        return groups

    def handle_groups(self, groups, *, move: bool, output_dir: str):
        out = Path(output_dir)
        out.mkdir(exist_ok=True)
        for idx, group in enumerate(groups, 1):
            Path(group[0])
            if move:
                for victim in group[1:]:
                    try:
                        print(victim)
                    except Exception as e:
                        print(f"Failed to delete {victim}: {e}")
            else:
                grp_dir = out / f"similarity_group_{idx}"
                grp_dir.mkdir(exist_ok=True)
                for p in group:
                    try:
                        shutil.copy2(p, grp_dir / Path(p).name)
                    except Exception as e:
                        print(f"Failed to copy {p}: {e}")

    def print_duplicates(self):
        if not self.duplicates:
            return
        print("\n" + "=" * 40)
        print("DUPLICATES (100% identical)")
        for h, paths in self.duplicates.items():
            print(f"\nHash: {h}")
            for p in paths:
                print(f"  - {p}")
        print("=" * 40)


def main():
    parser = argparse.ArgumentParser(description="Detect duplicate and similar files")
    parser.add_argument("threshold", type=int, default=70, help="Similarity threshold (0-100)")
    parser.add_argument(
        "-m", "--move", action="store_true", help="Keep one file per similarity group and delete the rest"
    )
    parser.add_argument("-o", "--output", default="output", help="Output directory (copy mode only)")
    args = parser.parse_args()
    detector = FileSimilarityDetector()
    files = list(detector.scan_files())
    if not files:
        print("No files found.")
        return
    detector.process_files(files)
    groups = detector.find_similarity_groups(args.threshold)
    if groups:
        detector.handle_groups(groups, move=args.move, output_dir=args.output)
        print(f"Processed {len(groups)} similarity groups.")
    else:
        print("No similar (non-identical) files found.")
    detector.print_duplicates()


if __name__ == "__main__":
    main()
