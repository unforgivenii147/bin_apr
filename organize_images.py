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
import shutil
from pathlib import Path

import cv2
import numpy as np


def get_image_features_cv2(image_path, size=(64, 64)):
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Could not read {image_path}")
            return None
        if img.size == 0:
            print(f"Warning: Empty image {image_path}")
            return None
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        img_resized = cv2.resize(img, size)
        hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
        try:
            hist_h = cv2.calcHist([hsv], [0], None, [8], [0][180])
            hist_s = cv2.calcHist([hsv], [1], None, [8], [0][256])
            hist_v = cv2.calcHist([hsv], [2], None, [8], [0][256])
        except cv2.error as e:
            print(f"Histogram calculation error for {image_path}: {e}")
            return None
        img_flat = img_resized.flatten()
        features = np.concatenate([hist_h.flatten(), hist_s.flatten(), hist_v.flatten(), img_flat])
        norm = np.linalg.norm(features)
        if norm > 0:
            features /= norm
        return features
    except Exception as e:
        print(f"Error processing {image_path}: {e!s}")
        return None


def get_all_images(directory):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    image_files = []
    for root, _dirs, files in os.walk(directory):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in image_extensions:
                full_path = os.path.join(root, file)
                if Path(full_path).is_file() and os.access(full_path, os.R_OK):
                    image_files.append(full_path)
    return image_files


def compute_similarity(feat1, feat2):
    if feat1 is None or feat2 is None:
        return 0.0
    norm1 = np.linalg.norm(feat1)
    norm2 = np.linalg.norm(feat2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(feat1, feat2) / (norm1 * norm2)


def simple_clustering(features, paths, n_clusters=10, threshold=0.7):
    n_samples = len(features)
    if n_samples == 0:
        return np.array([])
    clusters = {i: [i] for i in range(n_samples)}
    cluster_centers = {i: features[i].copy() for i in range(n_samples)}
    max_iterations = n_samples * 2
    iteration = 0
    while len(clusters) > n_clusters and iteration < max_iterations:
        iteration += 1
        max_sim = -1
        merge_pair = None
        cluster_ids = list(clusters.keys())
        for i in range(len(cluster_ids)):
            for j in range(i + 1, len(cluster_ids)):
                id1, id2 = (cluster_ids[i], cluster_ids[j])
                sim = compute_similarity(cluster_centers[id1], cluster_centers[id2])
                if sim > max_sim:
                    max_sim = sim
                    merge_pair = (id1, id2)
        if merge_pair is None or max_sim < threshold:
            break
        id1, id2 = merge_pair
        clusters[id1].extend(clusters[id2])
        indices = clusters[id1]
        cluster_features = [features[idx] for idx in indices]
        cluster_centers[id1] = np.mean(cluster_features, axis=0)
        del clusters[id2]
        del cluster_centers[id2]
    labels = np.zeros(n_samples, dtype=int)
    for cluster_id, (_key, indices) in enumerate(clusters.items()):
        for idx in indices:
            labels[idx] = cluster_id
    return labels


def organize_photos(source_dir=".", n_clusters=10, move=False, threshold=0.7):
    print(f"Scanning directory: {source_dir}")
    image_paths = get_all_images(source_dir)
    print(f"Found {len(image_paths)} images")
    if len(image_paths) == 0:
        print("No images found!")
        return
    print("Extracting features with OpenCV...")
    features = []
    valid_paths = []
    for i, path in enumerate(image_paths):
        if i % 10 == 0:
            print(f"Processing {i}/{len(image_paths)}...")
        feat = get_image_features_cv2(path)
        if feat is not None:
            features.append(feat)
            valid_paths.append(path)
    print(f"\nSuccessfully processed {len(features)} out of {len(image_paths)} images")
    if len(features) == 0:
        print("No valid images to process!")
        return
    features = np.array(features)
    n_clusters = min(n_clusters, len(features))
    print(f"Clustering into {n_clusters} groups...")
    labels = simple_clustering(features, valid_paths, n_clusters, threshold)
    output_base = os.path.join(source_dir, "organized_by_similarity")
    Path(output_base).mkdir(exist_ok=True, parents=True)
    print("Organizing files...")
    for label in range(n_clusters):
        cluster_dir = os.path.join(output_base, f"group_{label + 1}")
        Path(cluster_dir).mkdir(exist_ok=True, parents=True)
    for path, label in zip(valid_paths, labels, strict=False):
        dest_dir = os.path.join(output_base, f"group_{label + 1}")
        dest_path = os.path.join(dest_dir, Path(path).name)
        counter = 1
        base_name = Path(dest_path).stem
        extension = Path(dest_path).suffix
        while Path(dest_path).exists():
            dest_path = os.path.join(dest_dir, f"{base_name}_{counter}{extension}")
            counter += 1
        try:
            if move:
                shutil.move(path, dest_path)
            else:
                shutil.copy2(path, dest_path)
        except Exception as e:
            print(f"Error copying {path}: {e}")
    print(f"\nDone! Photos organized in: {output_base}")
    print(f"Organized {len(valid_paths)} images into {n_clusters} groups")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Organize photos by similarity")
    parser.add_argument("-d", "--directory", default=".", help="Source directory (default: current)")
    parser.add_argument("-k", "--clusters", type=int, default=10, help="Number of groups (default: 10)")
    parser.add_argument("-m", "--move", action="store_true", help="Move files instead of copy")
    parser.add_argument("-t", "--threshold", type=float, default=0.7, help="Similarity threshold (default: 0.7)")
    args = parser.parse_args()
    organize_photos(args.directory, args.clusters, args.move, args.threshold)
