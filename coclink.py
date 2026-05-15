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

import os
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNELS = {
    "Blueprint_CoC": "UCQJJGSWnPUCb8uKV_MoJeOA",
    "iTzu": "UCLKKvlo0yK8OgWvjCiZQ3sA",
    "Clash_Champs": "UC_mD8S6pWpSstY3mXJ9nEqw",
}


def get_videos(youtube, channel_id):
    past_date = (datetime.now(UTC) - timedelta(days=30)).isoformat()
    videos = []
    request = youtube.search().list(
        part="snippet", channelId=channel_id, publishedAfter=past_date, maxResults=50, order="date", type="video"
    )
    while request:
        response = request.execute()
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            video_details = youtube.videos().list(part="snippet", id=video_id).execute()
            snippet = video_details["items"][0]["snippet"]
            videos.append(
                {
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )
        request = youtube.search().list_next(request, response)
        if len(videos) > 100:
            break
    return videos


def extract_th18_links(description):
    pattern = "(https?://link\\.clashofclans\\.com/[^\\s]+)"
    links = re.findall(pattern, description)
    return [l for l in links if "TH18" in l.upper() or "TH18" in description.upper()]


def create_html(channel_name, base_data):
    date_str = datetime.now().strftime("%d-%m-%Y")
    dir_name = f"output/{date_str}_{channel_name}"
    Path(dir_name).mkdir(exist_ok=True, parents=True)
    file_path = os.path.join(dir_name, "bases.html")
    html_content = f"\n    <html>\n    <head>\n        <title>{channel_name} TH18 Bases</title>\n        <style>\n            body {{ font-family: sans-serif; padding: 20px; background:\n            .card {{ background: white; margin-bottom: 15px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}\n            a {{ color:\n            .vid-ref {{ font-size: 0.9em; color:\n        </style>\n    </head>\n    <body>\n        <h1>TH18 Bases from {channel_name} (Last 30 Days)</h1>\n    "
    for item in base_data:
        html_content += f'''\n        <div class="card">\n            <h3>{item["title"]}</h3>\n            <p class="vid-ref">Source: <a href="{item["video_url"]}" target="_blank">Watch Video</a></p>\n            <ul>\n        '''
        for link in item["links"]:
            html_content += f'<li><a href="{link}">Get Base Layout</a></li>'
        html_content += "</ul></div>"
    html_content += "</body></html>"
    Path(file_path).write_text(html_content, encoding="utf-8")
    print(f"Generated: {file_path}")


def main():
    if not API_KEY:
        print("Error: API_KEY not found in .env file.")
        return
    youtube = build("youtube", "v3", developerKey=API_KEY)
    for name, cid in CHANNELS.items():
        print(f"Processing {name}...")
        vids = get_videos(youtube, cid)
        results = []
        for v in vids:
            links = extract_th18_links(v["description"])
            if links:
                results.append({"title": v["title"], "video_url": v["url"], "links": list(set(links))})
        if results:
            create_html(name, results)
        else:
            print(f"No TH18 links found for {name}.")


if __name__ == "__main__":
    main()
