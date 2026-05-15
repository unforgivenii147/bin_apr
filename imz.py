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

from __future__ import annotations

import argparse
import ast
import contextlib
import json
import multiprocessing as mp
import os
import re
import sys
import tarfile
import zipfile
from pathlib import Path

import xxhash
from dh import PKG_MAPPING, STDLIB
from tqdm import tqdm

CACHE_FILE = ".reqcache.json"


def fast_hash(path: Path) -> str:
    try:
        h = xxhash.xxh64()
        stat = path.stat()
        h.update(str(stat.st_size).encode())
        h.update(str(int(stat.st_mtime)).encode())
        with Path(path).open("rb") as f:
            h.update(f.read())
        return h.hexdigest()
    except Exception:
        return "0"


def load_json(path: Path) -> dict:
    try:
        with Path(path).open(encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(path: Path, obj: dict) -> None:
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def load_set_file(path: str) -> set[str]:
    out = set()
    try:
        with Path(path).open(encoding="utf-8", errors="ignore") as f:
            for line in f:
                v = line.strip()
                if v:
                    out.add(v)
    except Exception:
        pass
    return out


def load_mapping(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    try:
        with Path(path).open(encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    out[k.strip()] = v.strip()
    except Exception:
        pass
    return out


def extract_from_ast(code: str, path_hint: str | None = None) -> dict[str, set[str]]:
    result = {"imports": set(), "star_modules": set(), "dynamic": set(), "relative": set()}
    try:
        tree = ast.parse(code)
    except Exception:
        for m in re.finditer("(?:import_module|__import__)\\(\\s*['\\\"]([\\w\\.]+)['\\\"]\\s*\\)", code):
            result["dynamic"].add(m.group(1).split(".", 1)[0])
        return result
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                first = a.name.split(".", 1)[0]
                result["imports"].add(first)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                if node.module:
                    result["relative"].add(node.module.split(".", 1)[0])
                else:
                    result["relative"].add(".")
                continue
            if node.module:
                base = node.module.split(".", 1)[0]
                if any((name.name == "*" for name in node.names)):
                    result["star_modules"].add(node.module)
                else:
                    result["imports"].add(base)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    result["dynamic"].add(node.args[0].value.split(".", 1)[0])
            elif isinstance(node.func, ast.Attribute):
                val = node.func
                if (
                    isinstance(val.value, ast.Name) and val.value.id == "importlib" and (val.attr == "import_module")
                ) and (node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                    result["dynamic"].add(node.args[0].value.split(".", 1)[0])
    return result


def process_py_file_content(code: str, path_hint: str | None = None) -> dict[str, list[str]]:
    d = extract_from_ast(code, path_hint)
    return {k: sorted(v) for k, v in d.items()}


def process_py_file(path: Path) -> dict[str, list[str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"imports": [], "star_modules": [], "dynamic": [], "relative": []}
    return process_py_file_content(text, str(path))


def process_noext_python_script(path: Path) -> dict[str, list[str]]:
    try:
        with Path(path).open(encoding="utf-8", errors="ignore") as f:
            first = f.readline()
            if "#!" not in first or "python" not in first.lower():
                return {"imports": [], "star_modules": [], "dynamic": [], "relative": []}
            code = f.read()
    except Exception:
        return {"imports": [], "star_modules": [], "dynamic": [], "relative": []}
    return process_py_file_content(code, str(path))


def process_ipynb(path: Path) -> dict[str, list[str]]:
    out = {"imports": [], "star_modules": [], "dynamic": [], "relative": []}
    try:
        with Path(path).open(encoding="utf-8", errors="ignore") as f:
            nb = json.load(f)
    except Exception:
        return out
    imports = set()
    stars = set()
    dyn = set()
    rel = set()
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            d = extract_from_ast(src, str(path))
            imports |= d["imports"]
            stars |= d["star_modules"]
            dyn |= d["dynamic"]
            rel |= d["relative"]
    out["imports"] = sorted(imports)
    out["star_modules"] = sorted(stars)
    out["dynamic"] = sorted(dyn)
    out["relative"] = sorted(rel)
    return out


def process_zip_file(path: Path) -> dict[str, list[str]]:
    imports = set()
    stars = set()
    dyn = set()
    rel = set()
    try:
        with zipfile.ZipFile(path, "r") as z:
            for name in z.namelist():
                if name.endswith(".py"):
                    try:
                        code = z.read(name).decode("utf-8", errors="ignore")
                        d = extract_from_ast(code, f"{path}:{name}")
                        imports |= d["imports"]
                        stars |= d["star_modules"]
                        dyn |= d["dynamic"]
                        rel |= d["relative"]
                    except Exception:
                        pass
    except Exception:
        pass
    return {"imports": sorted(imports), "star_modules": sorted(stars), "dynamic": sorted(dyn), "relative": sorted(rel)}


def process_tar_file(path: Path) -> dict[str, list[str]]:
    imports = set()
    stars = set()
    dyn = set()
    rel = set()
    mode = "r:xz" if str(path).endswith(".xz") else "r:gz"
    try:
        with tarfile.open(path, mode) as t:
            for m in t.getmembers():
                if m.isfile() and m.name.endswith(".py"):
                    try:
                        f = t.extractfile(m)
                        if not f:
                            continue
                        code = f.read().decode("utf-8", errors="ignore")
                        d = extract_from_ast(code, f"{path}:{m.name}")
                        imports |= d["imports"]
                        stars |= d["star_modules"]
                        dyn |= d["dynamic"]
                        rel |= d["relative"]
                    except Exception:
                        pass
    except Exception:
        pass
    return {"imports": sorted(imports), "star_modules": sorted(stars), "dynamic": sorted(dyn), "relative": sorted(rel)}


def process_raw(path: str) -> dict[str, list[str]]:
    p = Path(path)
    name = str(p).lower()
    if p.suffix == ".py":
        return process_py_file(p)
    if p.suffix == ".ipynb":
        return process_ipynb(p)
    if p.suffix == "" and p.is_file():
        return process_noext_python_script(p)
    if name.endswith((".zip", ".whl")):
        return process_zip_file(p)
    if name.endswith((".tar.gz", ".tgz", ".tar.xz")):
        return process_tar_file(p)
    return {"imports": [], "star_modules": [], "dynamic": [], "relative": []}


def build_project_module_map(sources: list[str]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for fp in sources:
        p = Path(fp)
        if not p.exists():
            continue
        if p.suffix != ".py":
            continue
        rel = os.path.normpath(fp).lstrip("./")
        parts = rel.split(os.sep)
        if parts[-1] == "__init__.py":
            mod = ".".join(parts[:-1]) if parts[:-1] else parts[-2] if len(parts) > 1 else ""
        else:
            mod = ".".join(parts)[:-3] if rel.endswith(".py") else ".".join(parts)
        if not mod:
            continue
        top = mod.split(".", 1)[0]
        mapping.setdefault(mod, []).append(fp)
        mapping.setdefault(top, [*mapping.get(top, []), fp])
    return mapping


def trace_star_module(module: str, project_map: dict[str, list[str]]) -> set[str]:
    found_imports = set()
    candidates = []
    if module in project_map:
        candidates += project_map[module]
    top = module.split(".", 1)[0]
    if top in project_map:
        candidates += project_map[top]
    candidates = list(dict.fromkeys(candidates))
    for fp in candidates:
        try:
            text = Path(fp).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        d = extract_from_ast(text, fp)
        found_imports |= d["imports"]
        found_imports |= {m.split(".", 1)[0] for m in d["dynamic"]}
        try:
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            val = node.value
                            names = []
                            if isinstance(val, (ast.List, ast.Tuple)):
                                names.extend(
                                    (
                                        elt.value
                                        for elt in val.elts
                                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                                    )
                                )
                            for nm in names:
                                if "." in nm:
                                    found_imports.add(nm.split(".", 1)[0])
        except Exception:
            pass
    return found_imports


def resolve_packages(
    imports: set[str], stdlib: set[str], mapping: dict[str, str], pip_available: set[str], project_toplevels: set[str]
) -> set[str]:
    out = set()
    for imp in imports:
        if not imp:
            continue
        if imp in stdlib:
            continue
        if imp in project_toplevels:
            continue
        if imp in mapping:
            out_name = mapping[imp]
        else:
            parts = imp.split(".")
            mapped = None
            for i in range(len(parts), 0, -1):
                key = ".".join(parts[:i])
                if key in mapping:
                    mapped = mapping[key]
                    break
            out_name = mapped or parts[0]
        if pip_available:
            low = {p.lower(): p for p in pip_available}
            candidate_low = out_name.lower()
            if candidate_low in low:
                out.add(low[candidate_low])
                continue
        out.add(out_name)
    return out


def scan_sources(ignore_dirs: set[str]) -> list[str]:
    out = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in files:
            fp = os.path.join(root, f)
            lower = f.lower()
            if lower.endswith((".py", ".ipynb", ".whl", ".zip", ".tar.gz", ".tgz", ".tar.xz")) or Path(fp).suffix == "":
                out.append(fp)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Offline requirements.txt generator (static + heuristics).")
    p.add_argument(
        "--ignore", nargs="*", default=[".venv", ".git", ".ipynb_checkpoints"], help="Directories to ignore during scan"
    )
    p.add_argument("--no-cache", action="store_true", default=True, help="Disable cache usage")
    p.add_argument("--clear-cache", action="store_true", help="Clear cache and exit")
    p.add_argument("--pipfile", default="/sdcard/pip.txt", help="Offline pip package list (one per line)")
    p.add_argument("--cache-file", default=CACHE_FILE, help="Cache file path")
    p.add_argument("--out", default="requirements.txt", help="Output requirements file")
    p.add_argument(
        "--include-unknown",
        action="store_true",
        default=True,
        help="Include packages not present in offline pip list (default: only include those in piplist)",
    )
    args = p.parse_args()
    ignore_dirs = set(args.ignore)
    stdlib = STDLIB
    mapping = PKG_MAPPING
    piplist = load_set_file(args.pipfile)
    sources = scan_sources(ignore_dirs)
    sources = sorted(set(sources))
    project_map = build_project_module_map(sources)
    set(project_map.keys())
    project_top_only = {k.split(".", 1)[0] for k in project_map}
    cache_path = Path(args.cache_file)
    cache = {} if args.no_cache else load_json(cache_path) if cache_path.exists() else {}
    if args.clear_cache:
        try:
            if cache_path.exists():
                cache_path.unlink()
            print("Cache cleared.")
        except Exception as e:
            print("Failed clearing cache:", e)
        return
    tasks = []
    cached_results = []
    for path in sources:
        pth = Path(path)
        key = os.path.normpath(path)
        needs = True
        if not args.no_cache and key in cache:
            entry = cache[key]
            try:
                mtime = pth.stat().st_mtime
            except Exception:
                mtime = None
            h = fast_hash(pth) if mtime is not None else "0"
            if entry.get("mtime") == mtime and entry.get("hash") == h:
                cached_results.append(
                    entry.get("result", {"imports": [], "star_modules": [], "dynamic": [], "relative": []})
                )
                needs = False
        if needs:
            tasks.append(path)
    computed_results = []
    if tasks:
        with mp.Pool(mp.cpu_count()) as pool:
            for res in tqdm(pool.imap_unordered(process_raw, tasks), total=len(tasks), desc="Processing"):
                computed_results.append(res)
    if not args.no_cache:
        for path, res in zip(tasks, computed_results, strict=False):
            key = os.path.normpath(path)
            try:
                mtime = Path(path).stat().st_mtime
            except Exception:
                mtime = None
            h = fast_hash(Path(path)) if mtime is not None else "0"
            cache[key] = {"mtime": mtime, "hash": h, "result": res}
        with contextlib.suppress(Exception):
            save_json(cache_path, cache)
    all_imports: set[str] = set()
    all_star_modules: set[str] = set()
    all_dynamic: set[str] = set()
    all_relative: set[str] = set()
    for r in cached_results + computed_results:
        all_imports |= set(r.get("imports", []))
        all_star_modules |= set(r.get("star_modules", []))
        all_dynamic |= set(r.get("dynamic", []))
        all_relative |= set(r.get("relative", []))
    traced_from_star = set()
    if all_star_modules:
        for mod in tqdm(sorted(all_star_modules), desc="Tracing star imports"):
            traced_from_star |= trace_star_module(mod, project_map)
    dynamic_tops = {d.split(".", 1)[0] for d in all_dynamic}
    discovered = set(all_imports) | traced_from_star | dynamic_tops
    final_candidates = set()
    for imp in discovered:
        if not imp:
            continue
        if imp in stdlib:
            continue
        if imp in project_top_only:
            continue
        if imp in all_relative:
            continue
        final_candidates.add(imp)
    pkgs = resolve_packages(final_candidates, stdlib, mapping, piplist, project_top_only)
    if not args.include_unknown and piplist:
        lowpip = {p.lower() for p in piplist}
        pkgs = {p for p in pkgs if p.lower() in lowpip}
    out_file = Path(args.out)
    try:
        with out_file.open("w", encoding="utf-8") as f:
            for pkg in sorted(pkgs, key=lambda s: s.lower()):
                f.write(pkg + "\n")
    except Exception as e:
        print("Failed writing requirements file:", e)
        sys.exit(2)
    print("\nGenerated", out_file.name)
    print("────────────────────────────")
    if pkgs:
        for pkg in sorted(pkgs, key=lambda s: s.lower()):
            print(pkg)
    else:
        print("(empty)")


if __name__ == "__main__":
    main()
