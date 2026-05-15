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

import shutil
import subprocess
import sys


def run_git_command(cmd, check=True, capture_output=True):
    try:
        return subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return None


def is_git_repository():
    return run_git_command("git rev-parse --git-dir", check=False) is not None


def get_current_branch():
    result = run_git_command("git branch --show-current")
    if result and result.stdout:
        return result.stdout.strip()
    return None


def get_main_branch_name():
    result = run_git_command("git remote show origin", check=False)
    if result and "HEAD branch" in result.stdout:
        for line in result.stdout.split("\n"):
            if "HEAD branch" in line:
                return line.split(":")[1].strip()
    result = run_git_command("git branch -l")
    if result:
        branches = [b.strip().replace("* ", "") for b in result.stdout.split("\n") if b.strip()]
        for branch in branches:
            if branch in {"main", "master"}:
                return branch
    return "main"


def get_all_branches():
    result = run_git_command("git branch -l")
    if not result:
        return []
    branches = []
    for line in result.stdout.split("\n"):
        if line.strip():
            branch = line.strip().replace("* ", "")
            branches.append(branch)
    return branches


def delete_branches_except_main():
    main_branch = get_main_branch_name()
    branches = get_all_branches()
    print(f"Main branch: {main_branch}")
    print(f"Found branches: {', '.join(branches)}")
    deleted_branches = []
    for branch in branches:
        if branch != main_branch:
            print(f"Deleting branch: {branch}")
            result = run_git_command(f"git branch -D {branch}", check=False)
            if result and result.returncode == 0:
                deleted_branches.append(branch)
                print(f"✓ Deleted branch: {branch}")
            else:
                print(f"✗ Failed to delete branch: {branch}")
    return deleted_branches


def reset_to_last_commit() -> bool:
    print("Resetting to last commit...")
    result = run_git_command("git rev-parse HEAD")
    if not result:
        return False
    current_commit = result.stdout.strip()
    print(f"Current commit: {current_commit}")
    main_branch = get_main_branch_name()
    commands = [
        "git checkout --orphan temp_branch",
        "git add -A",
        'git commit -m "Squashed history - only keeping last commit"',
        f"git branch -D {main_branch}",
        f"git branch -m {main_branch}",
    ]
    for cmd in commands:
        print(f"Running: {cmd}")
        result = run_git_command(cmd, check=False)
        if not result or result.returncode != 0:
            print(f"Failed to run: {cmd}")
            return False
    print("✓ Successfully reset to last commit")
    return True


def alternative_reset_method() -> None:
    print("Using alternative reset method...")
    commands = [
        "git branch backup-before-cleanup",
        "git reset --hard HEAD",
        "git reflog expire --expire=now --all",
        "git gc --prune=now --aggressive",
    ]
    for cmd in commands:
        print(f"Running: {cmd}")
        result = run_git_command(cmd, check=False)
        if not result or result.returncode != 0:
            print(f"Warning: Command failed: {cmd}")
    print("✓ Alternative reset completed")


def create_backup() -> bool | None:
    backup_dir = f"git_backup_{subprocess.getoutput('date +%Y%m%d_%H%M%S')}"
    print(f"Creating backup in: {backup_dir}")
    try:
        shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(".git"))
        print(f"✓ Backup created: {backup_dir}")
        return True
    except Exception as e:
        print(f"✗ Failed to create backup: {e}")
        return False


def main() -> None:
    print("=" * 60)
    print("GIT REPOSITORY CLEANER")
    print("WARNING: This is a DESTRUCTIVE operation!")
    print("It will delete all commits except the last one")
    print("and delete all branches except main/master.")
    print("=" * 60)
    if not is_git_repository():
        print("Error: Not a git repository!")
        sys.exit(1)
    response = input("\nAre you sure you want to continue? (yes/NO): ")
    if response.lower() not in {"yes", "y"}:
        print("Operation cancelled.")
        sys.exit(0)
    print("\n1. Creating backup...")
    if not create_backup():
        response = input("Backup failed. Continue anyway? (yes/NO): ")
        if response.lower() not in {"yes", "y"}:
            print("Operation cancelled.")
            sys.exit(0)
    print("\n2. Checking repository status...")
    main_branch = get_main_branch_name()
    current_branch = get_current_branch()
    branches = get_all_branches()
    print(f"   Current branch: {current_branch}")
    print(f"   Main branch: {main_branch}")
    print(f"   All branches: {', '.join(branches)}")
    if current_branch != main_branch:
        print(f"\n3. Switching to main branch: {main_branch}")
        result = run_git_command(f"git checkout {main_branch}", check=False)
        if not result or result.returncode != 0:
            print(f"Failed to switch to {main_branch}")
            sys.exit(1)
    print(f"\n4. Deleting branches except {main_branch}...")
    deleted_branches = delete_branches_except_main()
    if deleted_branches:
        print(f"   Deleted {len(deleted_branches)} branches")
    else:
        print("   No branches to delete")
    print("\n5. Resetting ...")
    if not alternative_reset_method():
        reset_to_last_commit()
    print("\n6. Final status:")
    result = run_git_command("git log --oneline")
    if result:
        print("   Commit history:")
        for line in result.stdout.strip().split("\n"):
            print(f"     {line}")
    branches = get_all_branches()
    print(f"   Remaining branches: {', '.join(branches)}")
    print("\n✓ Cleanup completed!")
    print("⚠️  Remember: You may need to force push to remote:")
    print(f"   git push --force origin {main_branch}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error : {e}")
        sys.exit(1)
