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
import json
import typing as T
from copy import deepcopy
from pathlib import Path

T_None = type(None)
root: dict


def assert_has_typed_keys(path: str, data: dict, keys: T.Dict[str, T.Any]) -> dict:
    assert set(data.keys()).issuperset(keys.keys()), f"{path}: DIFF: {set(data.keys()).difference(keys.keys())}"
    res = dict()
    for key, val in keys.items():
        cur = data.pop(key)
        assert isinstance(cur, val), f"{path}: type({key}: {cur}) != {val}"
        res[key] = cur
    return res


def validate_base_obj(path: str, name: str, obj: dict) -> None:
    expected: T.Dict[str, T.Any] = {
        "name": str,
        "description": str,
        "since": (str, T_None),
        "deprecated": (str, T_None),
        "notes": list,
        "warnings": list,
    }
    cur = assert_has_typed_keys(f"{path}.{name}", obj, expected)
    assert cur["name"], f"{path}.{name}"
    assert cur["description"], f"{path}.{name}"
    assert cur["name"] == name, f"{path}.{name}"
    assert all((isinstance(x, str) and x for x in cur["notes"])), f"{path}.{name}"
    assert all((isinstance(x, str) and x for x in cur["warnings"])), f"{path}.{name}"


def validate_type(path: str, typ: dict) -> None:
    expected: T.Dict[str, T.Any] = {"obj": str, "holds": list}
    cur = assert_has_typed_keys(path, typ, expected)
    assert not typ, f"{path} has extra keys: {typ.keys()}"
    assert cur["obj"] in root["objects"], path
    for i in cur["holds"]:
        validate_type(path, i)


def validate_arg(path: str, name: str, arg: dict) -> None:
    validate_base_obj(path, name, arg)
    expected: T.Dict[str, T.Any] = {
        "type": list,
        "type_str": str,
        "required": bool,
        "default": (str, T_None),
        "min_varargs": (int, T_None),
        "max_varargs": (int, T_None),
    }
    cur = assert_has_typed_keys(f"{path}.{name}", arg, expected)
    assert not arg, f"{path}.{name} has extra keys: {arg.keys()}"
    assert cur["type"], f"{path}.{name}"
    assert cur["type_str"], f"{path}.{name}"
    for i in cur["type"]:
        validate_type(f"{path}.{name}", i)
    if cur["min_varargs"] is not None:
        assert cur["min_varargs"] > 0, f"{path}.{name}"
    if cur["max_varargs"] is not None:
        assert cur["max_varargs"] > 0, f"{path}.{name}"


def validate_function(path: str, name: str, func: dict) -> None:
    validate_base_obj(path, name, func)
    expected: T.Dict[str, T.Any] = {
        "returns": list,
        "returns_str": str,
        "example": (str, T_None),
        "posargs": dict,
        "optargs": dict,
        "kwargs": dict,
        "varargs": (dict, T_None),
        "arg_flattening": bool,
    }
    cur = assert_has_typed_keys(f"{path}.{name}", func, expected)
    assert not func, f"{path}.{name} has extra keys: {func.keys()}"
    assert cur["returns"], f"{path}.{name}"
    assert cur["returns_str"], f"{path}.{name}"
    for i in cur["returns"]:
        validate_type(f"{path}.{name}", i)
    for k, v in cur["posargs"].items():
        validate_arg(f"{path}.{name}", k, v)
    for k, v in cur["optargs"].items():
        validate_arg(f"{path}.{name}", k, v)
    for k, v in cur["kwargs"].items():
        validate_arg(f"{path}.{name}", k, v)
    if cur["varargs"]:
        validate_arg(f"{path}.{name}", cur["varargs"]["name"], cur["varargs"])


def validate_object(path: str, name: str, obj: dict) -> None:
    validate_base_obj(path, name, obj)
    expected: T.Dict[str, T.Any] = {
        "example": (str, T_None),
        "object_type": str,
        "methods": dict,
        "is_container": bool,
        "extends": (str, T_None),
        "returned_by": list,
        "extended_by": list,
        "defined_by_module": (str, T_None),
    }
    cur = assert_has_typed_keys(f"{path}.{name}", obj, expected)
    assert not obj, f"{path}.{name} has extra keys: {obj.keys()}"
    for key, val in cur["methods"].items():
        validate_function(f"{path}.{name}", key, val)
    if cur["extends"] is not None:
        assert cur["extends"] in root["objects"], f"{path}.{name}"
    assert all((isinstance(x, str) for x in cur["returned_by"])), f"{path}.{name}"
    assert all((isinstance(x, str) for x in cur["extended_by"])), f"{path}.{name}"
    assert all((x in root["objects"] for x in cur["extended_by"])), f"{path}.{name}"
    if cur["defined_by_module"] is not None:
        assert cur["defined_by_module"] in root["objects"], f"{path}.{name}"
        assert cur["object_type"] == "RETURNED", f"{path}.{name}"
        assert root["objects"][cur["defined_by_module"]]["object_type"] == "MODULE", f"{path}.{name}"
        assert name in root["objects_by_type"]["modules"][cur["defined_by_module"]], f"{path}.{name}"
        return
    assert cur["object_type"] in {"ELEMENTARY", "BUILTIN", "MODULE", "RETURNED"}, f"{path}.{name}"
    if cur["object_type"] == "ELEMENTARY":
        assert name in root["objects_by_type"]["elementary"], f"{path}.{name}"
    if cur["object_type"] == "BUILTIN":
        assert name in root["objects_by_type"]["builtins"], f"{path}.{name}"
    if cur["object_type"] == "RETURNED":
        assert name in root["objects_by_type"]["returned"], f"{path}.{name}"
    if cur["object_type"] == "MODULE":
        assert name in root["objects_by_type"]["modules"], f"{path}.{name}"


def main() -> int:
    global root
    parser = argparse.ArgumentParser(description="Meson JSON docs validator")
    parser.add_argument("doc_file", type=Path, help="The JSON docs to validate")
    args = parser.parse_args()
    root_tmp = json.loads(args.doc_file.read_text(encoding="utf-8"))
    root = deepcopy(root_tmp)
    assert isinstance(root, dict)
    expected: T.Dict[str, T.Any] = {
        "version_major": int,
        "version_minor": int,
        "meson_version": str,
        "functions": dict,
        "objects": dict,
        "objects_by_type": dict,
    }
    cur = assert_has_typed_keys("root", root_tmp, expected)
    assert not root_tmp, f"root has extra keys: {root_tmp.keys()}"
    refs = cur["objects_by_type"]
    expected = {"elementary": list, "builtins": list, "returned": list, "modules": dict}
    assert_has_typed_keys(f"root.objects_by_type", refs, expected)
    assert not refs, f"root.objects_by_type has extra keys: {refs.keys()}"
    assert all((isinstance(x, str) for x in root["objects_by_type"]["elementary"]))
    assert all((isinstance(x, str) for x in root["objects_by_type"]["builtins"]))
    assert all((isinstance(x, str) for x in root["objects_by_type"]["returned"]))
    assert all((isinstance(x, str) for x in root["objects_by_type"]["modules"]))
    assert all((x in root["objects"] for x in root["objects_by_type"]["elementary"]))
    assert all((x in root["objects"] for x in root["objects_by_type"]["builtins"]))
    assert all((x in root["objects"] for x in root["objects_by_type"]["returned"]))
    assert all((x in root["objects"] for x in root["objects_by_type"]["modules"]))
    assert all((root["objects"][x]["object_type"] == "ELEMENTARY" for x in root["objects_by_type"]["elementary"]))
    assert all((root["objects"][x]["object_type"] == "BUILTIN" for x in root["objects_by_type"]["builtins"]))
    assert all((root["objects"][x]["object_type"] == "RETURNED" for x in root["objects_by_type"]["returned"]))
    assert all((root["objects"][x]["object_type"] == "MODULE" for x in root["objects_by_type"]["modules"]))
    assert all((all((isinstance(x, str) for x in v)) for k, v in root["objects_by_type"]["modules"].items()))
    assert all((all((x in root["objects"] for x in v)) for k, v in root["objects_by_type"]["modules"].items()))
    assert all(
        (
            all((root["objects"][x]["defined_by_module"] == k for x in v))
            for k, v in root["objects_by_type"]["modules"].items()
        )
    )
    for key, val in cur["functions"].items():
        validate_function("root", key, val)
    for key, val in cur["objects"].items():
        validate_object("root", key, val)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
