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

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from dh import runcmd

GITHUB_API_URL = "https://api.github.com/repos"
remained = []
GITHUB_TOKEN = None


def parse_repo_url(url_or_path):
    if "/" in url_or_path and (not url_or_path.startswith("http")):
        parts = url_or_path.strip().split("/")
        if len(parts) == 2 and parts[0] and parts[1]:
            return (parts[0], parts[1])
        return (None, None)
    try:
        parsed = urlparse(url_or_path.strip())
        if parsed.netloc.lower() in {"github.com", "www.github.com"}:
            path_parts = [p for p in parsed.path.split("/") if p]
            if len(path_parts) == 2:
                return (path_parts[0], path_parts[1])
    except Exception:
        pass
    return (None, None)


def get_repo_size_mb(user, repo):
    api_endpoint = f"{GITHUB_API_URL}/{user}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    try:
        response = requests.get(api_endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        size_bytes = data.get("size")
        if size_bytes is not None:
            size_mb = size_bytes / 1024.0
            return round(size_mb, 2)
        print(f"⚠️ Warning: Could not retrieve size for {user}/{repo} from API.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e.response.status_code} for {user}/{repo}")
        if e.response.status_code == 404:
            print("   Repository not found or access denied.")
        elif e.response.status_code == 403:
            print("   Rate limit exceeded or insufficient permissions.")
        else:
            print(f"   Response: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: Could not connect to GitHub API: {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred while fetching size: {e}")
        return None


def clone_repo_shallow(user, repo):
    repo_name = f"{user}/{repo}"
    repo_url = f"https://github.com/{repo_name}.git"
    clone_path = os.path.join(Path.cwd(), repo)
    if Path(clone_path).exists():
        return False
    print(f"\n🚀 Cloning {repo_name} (shallow clone)...")
    command = ["git", "clone", repo_url, clone_path]
    try:
        process = runcmd(command, show_output=True)
        print("✅ Successfully cloned repository.")
        print(f"   Cloned into: {clone_path}")
        return True
    except FileNotFoundError:
        print("❌ Error: 'git' command not found. Please ensure Git is installed and in your PATH.")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during cloning: {e}")
        return False


def process_repo(url):
    global remained
    user, repo = parse_repo_url(url)
    if not user or not repo:
        print(f"❌ Invalid GitHub repository format: '{repo_input}'")
        sys.exit(1)
    print(f"🔍 Analyzing repository: {user}/{repo}")
    repo_size = get_repo_size_mb(user, repo)
    if repo_size is not None and repo_size <= 100:
        print(f"ℹ️ size: {repo_size} MB")
        if clone_repo_shallow(user, repo):
            print("\n🎉 Done!")
            return
        print("\nScript finished with errors during cloning.")
        return
    remained.append(url)


'\n    if repo_size is not None and repo_size > 2.0:\n        cprint(f"ℹ️ size: {repo_size} MB", "cyan")\n        confirm = input(f"clone \'{user}/{repo}\'? (y/N): ").strip().lower()\n        if confirm == "y" or confirm == "yes":\n            if clone_repo_shallow(user, repo):\n                print("\n🎉 Done!")\n                return\n            else:\n                print("\nScript finished with errors during cloning.")\n                return\n        else:\n            print("Aborted cloning.")\n    else:\n        print("\nCould not proceed with cloning due to previous errors.")\n        return\n    return\n'
if __name__ == "__main__":
    repo_file = Path("repos.txt")
    content = repo_file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=False)
    i = 0
    ll = len(lines)
    for line in lines:
        print(f"{i}/{ll}")
        i += 1
        process_repo(line)
    Path("remained").write_text("\n".join(remained), encoding="utf-8")
