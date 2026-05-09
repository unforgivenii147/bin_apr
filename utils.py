#!/data/data/com.termux/files/usr/bin/python

DIRECTORY = "."
DIRECTORY = "."
DIRECTORY = "."
DIRECTORY = "."
DIRECTORY = "."
DIRECTORY = "."
DIRECTORY = "."
CHUNK_SIZE = 2000
CHUNK_SIZE = 2000
CHUNK_SIZE = 2000
CHUNK_SIZE = 2000
CHUNK_SIZE = 2000
CHUNK_SIZE = 2000
CHUNK_SIZE = 2000


def split_into_chunks(text: str, size: int):
    return [text[i : i + size] for i in range(0, len(text), size)]


def split_into_chunks(text: str, size: int):
    return [text[i : i + size] for i in range(0, len(text), size)]


def read_file(path):
    try:
        with Path(path).open(encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def extract_words(text):
    return re.findall("[a-z]{3,}", text.lower())


NUM_PROCESSES = 4
NUM_PROCESSES = 4


def main():
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = []
    if args:
        for arg in args:
            p = Path(arg)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                files.extend(get_files(p, extensions=[".png", ".PNG"]))
    else:
        files = get_files(root_dir, extensions=[".png", ".PNG"])
    _ = mpf3(process_file, files)


def main():
    root_dir = Path.cwd()
    args = sys.argv[1:]
    files = []
    if args:
        for arg in args:
            p = Path(arg)
            if p.is_file():
                files.append(p)
            elif p.is_dir():
                files.extend(get_files(p, extensions=[".png", ".PNG"]))
    else:
        files = get_files(root_dir, extensions=[".png", ".PNG"])
    _ = mpf3(process_file, files)


def random_key(length=32):
    return "".join((random.choice(string.ascii_letters + string.digits) for _ in range(length)))


def decrypt_file(file_path, key):
    backend = default_backend()
    raw = Path(file_path).read_bytes()
    iv = raw[:AES_BLOCK_SIZE]
    ciphertext = raw[AES_BLOCK_SIZE:]
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    Path(file_path).write_bytes(data)


def fetch_content_length(url: str) -> int | None:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            length = response.headers.get("Content-Length")
            if length:
                return int(length)
    except urllib.error.HTTPError as e:
        if e.code not in {405, 403}:
            raise
    request = urllib.request.Request(url, method="GET")
    request.add_header("Range", "bytes=0-0")
    with urllib.request.urlopen(request, timeout=10) as response:
        length = response.headers.get("Content-Length")
        return int(length) if length else None


def fsz(size_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16
MAX_QUEUE = 16


def parse_minutes() -> float:
    if len(sys.argv) == 1:
        return 60.0
    try:
        return float(sys.argv[1])
    except ValueError:
        print("Invalid argument. Usage: script.py [minutes]")
        sys.exit(1)


def get_all_files(root="."):
    file_paths = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            file_paths.append(full_path)
    return file_paths


def get_all_files(root="."):
    file_paths = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            file_paths.append(full_path)
    return file_paths


def get_all_files(root="."):
    file_paths = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            file_paths.append(full_path)
    return file_paths


def compute_hashes(files):
    hashes = {}
    for f in files:
        try:
            with Path(f).open("rb") as fh:
                data = fh.read()
                hashes[f] = ssdeep.hash(data)
        except Exception as e:
            print(f"Skipping {f}: {e}")
    return hashes


def group_similar_files(hashes, threshold):
    visited = set()
    groups = []
    files = list(hashes.keys())
    for i, f1 in enumerate(files):
        if f1 in visited:
            continue
        group = [f1]
        visited.add(f1)
        for f2 in files[i + 1 :]:
            if f2 in visited:
                continue
            score = ssdeep.compare(hashes[f1], hashes[f2])
            if score >= threshold:
                group.append(f2)
                visited.add(f2)
        if len(group) > 1:
            groups.append(group)
    return groups


DICT_FILE = "/sdcard/dic/dic.json"


def load_dictionary(path: Path):
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    fa_en = {str(k).strip(): str(v).strip() for k, v in data.items()}
    en_fa = {v: k for k, v in fa_en.items()}
    return (fa_en, en_fa)


def setup_readline(words):
    words = sorted(words)

    def completer(text, state):
        matches = [w for w in words if w.startswith(text)]
        return matches[state] if state < len(matches) else None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(" \t\n")


def translate(word, fa_en, en_fa):
    if word in fa_en:
        return fa_en[word]
    if word in en_fa:
        return en_fa[word]
    return None


def prefix_search(prefix, all_words):
    return sorted((w for w in all_words if w.startswith(prefix)))


def fuzzy_search(word, all_words, limit=5, cutoff=0.6):
    return get_close_matches(word, all_words, n=limit, cutoff=cutoff)


def interactive_mode(fa_en, en_fa):
    all_words = set(fa_en) | set(en_fa)
    setup_readline(all_words)
    print("Offline Persian ↔ English Translator")
    print("TAB for suggestions, Ctrl+C to exit\n")
    while True:
        try:
            word = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break
        if not word:
            continue
        result = translate(word, fa_en, en_fa)
        print(result or "Not found")


def get_unique_filepath(base_path: Path) -> Path:
    if not base_path.exists():
        return base_path
    name = base_path.stem
    suffix = base_path.suffix
    i = 1
    while True:
        new_path = base_path.with_name(f"{name}_{i}{suffix}")
        if not new_path.exists():
            return new_path
        i += 1


def save_entity(entity: dict[str, Any]):
    filename_base = f"{entity['full_name']}.py"
    output_path_base = OUTPUT_DIR / entity["type"] / filename_base
    output_path_base.parent.mkdir(parents=True, exist_ok=True)
    content = entity["code"]
    final_py_path = get_unique_filepath(output_path_base)
    try:
        Path(final_py_path).write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"Error saving {final_py_path}: {e}")
        return


def extract_entities_from_content(content: str, path: Path) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(content)
        extractor = EntityExtractor(content, path)
        extractor.visit(tree)
        return extractor.entities
    except SyntaxError:
        return []
    except Exception as e:
        print(f"Error parsing AST for {path}: {e}")
        return []


def extract_entities_from_content(content: str, path: Path) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(content)
        extractor = EntityExtractor(content, path)
        extractor.visit(tree)
        return extractor.entities
    except SyntaxError:
        return []
    except Exception as e:
        print(f"Error parsing AST for {path}: {e}")
        return []


def is_python_file_no_extension(path: Path) -> bool:
    if path.suffix:
        return False
    try:
        with Path(path).open(encoding="utf-8", errors="ignore") as f:
            first_lines = "".join(f.readlines(1024))
            if re.match("#!\\s*/.*python", first_lines):
                return True
            if "def " in first_lines or "class " in first_lines or "import " in first_lines:
                return True
    except:
        pass
    return False


def process_single_file(path: Path) -> list[dict[str, Any]]:
    try:
        if path.suffix == ".py" or is_python_file_no_extension(path):
            content = path.read_text(encoding="utf-8", errors="ignore")
            return extract_entities_from_content(content, path)
        return []
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return []


def process_single_file(path: Path) -> list[dict[str, Any]]:
    try:
        if path.suffix == ".py" or is_python_file_no_extension(path):
            content = path.read_text(encoding="utf-8", errors="ignore")
            return extract_entities_from_content(content, path)
        return []
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return []


def process_archive(path: Path) -> list[dict[str, Any]]:
    entities = []
    if path.suffix == ".zst":
        try:
            dctx = zstd.ZstdDecompressor()
            content = dctx.decompress(path.read_bytes()).decode("utf-8", errors="ignore")
            return extract_entities_from_content(content, path)
        except Exception as e:
            print(f"Error decompressing ZST file {path}: {e}")
            return []
    if path.suffix in {".zip", ".whl"}:
        try:
            with zipfile.ZipFile(path, "r") as zf:
                for member in zf.namelist():
                    member_path = Path(member)
                    if member_path.suffix == ".py":
                        with zf.open(member) as member_file:
                            content = member_file.read().decode("utf-8", errors="ignore")
                            virtual_path = Path(f"{path}/{member}")
                            entities.extend(extract_entities_from_content(content, virtual_path))
        except Exception as e:
            print(f"Error processing ZIP/WHL archive {path}: {e}")
    elif any((path.name.endswith(ext) for ext in [".tar", ".tar.gz", ".tgz", ".tar.zst", ".tar.xz"])):
        mode_map = {".tar.gz": "r:gz", ".tgz": "r:gz", ".tar.zst": "r:zst", ".tar.xz": "r:xz", ".tar": "r"}
        mode = next((mode_map[ext] for ext in mode_map if path.name.endswith(ext)), "r")
        try:
            with tarfile.open(path, mode) as tf:
                for member in tf.getmembers():
                    member_path = Path(member.name)
                    if member.isfile() and member_path.suffix == ".py":
                        member_file = tf.extractfile(member)
                        if member_file:
                            content = member_file.read().decode("utf-8", errors="ignore")
                            virtual_path = Path(f"{path}/{member.name}")
                            entities.extend(extract_entities_from_content(content, virtual_path))
        except tarfile.ReadError:
            pass
        except Exception as e:
            print(f"Error processing TAR archive {path}: {e}")
    return entities


def worker_process(path_str: str) -> list[dict[str, Any]]:
    path = Path(path_str)
    if path.name.endswith(ARCHIVE_EXTENSIONS):
        return process_archive(path)
    return process_single_file(path)


def get_current_folder_name():
    return Path(Path.cwd()).name


def folder_exists_in_db(cursor, folder_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (folder_name,))
    return cursor.fetchone() is not None


def get_imports_from_file(file_path):
    imports = set()
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update((n.name.split(".")[0] for n in node.names))
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports.add(node.module.split(".")[0])
    except (SyntaxError, UnicodeDecodeError):
        pass
    return imports


def copy_groups(groups, output_dir="output") -> None:
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    for idx, group in enumerate(groups, start=1):
        group_dir = os.path.join(output_dir, f"group_{idx}")
        Path(group_dir).mkdir(exist_ok=True, parents=True)
        for f in group:
            try:
                shutil.move(f, group_dir)
            except Exception as e:
                print(f"Failed to copy {f}: {e}")


def copy_groups(groups, output_dir="output") -> None:
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    for idx, group in enumerate(groups, start=1):
        group_dir = os.path.join(output_dir, f"group_{idx}")
        Path(group_dir).mkdir(exist_ok=True, parents=True)
        for f in group:
            try:
                shutil.move(f, group_dir)
            except Exception as e:
                print(f"Failed to copy {f}: {e}")


def write_report(groups, format="csv", output_dir="output") -> None:
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    if format == "csv":
        report_file = os.path.join(output_dir, "similar_report.csv")
        with Path(report_file).open("w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Group", "File"])
            for idx, group in enumerate(groups, start=1):
                for f in group:
                    writer.writerow([idx, f])
        print(f"CSV report written to {report_file}")
    elif format == "json":
        report_file = os.path.join(output_dir, "similar_report.json")
        data = {f"group_{idx}": group for idx, group in enumerate(groups, start=1)}
        with Path(report_file).open("w", encoding="utf-8") as jf:
            json.dump(data, jf, indent=2)
        print(f"JSON report written to {report_file}")


def colorize_score(score, threshold):
    if not USE_COLOR or score == "":
        return str(score)
    if score == 100 or score >= threshold + 10:
        return Fore.GREEN + str(score) + Style.RESET_ALL
    if score >= threshold:
        return Fore.YELLOW + str(score) + Style.RESET_ALL
    return Fore.RED + str(score) + Style.RESET_ALL


def write_matrix(hashes, threshold, output_dir="output", pretty=False) -> None:
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    files = list(hashes.keys())
    matrix_file = os.path.join(output_dir, "similarity_matrix.csv")
    table = [["File", *files]]
    with Path(matrix_file).open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File", *files])
        for f1 in files:
            row = [f1]
            for f2 in files:
                if f1 == f2:
                    score = 100
                else:
                    score = ssdeep.compare(hashes[f1], hashes[f2])
                    score = score if score >= threshold else ""
                row.append(score)
            writer.writerow(row)
            table.append(row)
    print(f"Threshold-filtered similarity matrix written to {matrix_file}")
    if pretty:
        if USE_TABULATE:
            colored_table = []
            for row in table[1:]:
                colored_row = [row[0]] + [colorize_score(cell, threshold) for cell in row[1:]]
                colored_table.append(colored_row)
            print(tabulate(colored_table, headers=table[0], tablefmt="grid"))
        else:
            header = " | ".join(table[0])
            print(header)
            print("-" * len(header))
            for row in table[1:]:
                formatted = [row[0]] + [colorize_score(cell, threshold) for cell in row[1:]]
                print(" | ".join((str(x) if x else "." for x in formatted)))


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <threshold> [copy|csv|json|matrix]")
        sys.exit(1)
    try:
        threshold = int(sys.argv[1])
    except ValueError:
        print("Threshold must be an integer (0–100).")
        sys.exit(1)
    mode = sys.argv[2] if len(sys.argv) > 2 else "copy"
    files = get_all_files(".")
    print(f"Found {len(files)} files. Computing hashes...")
    hashes = compute_hashes(files)
    print("Comparing files...")
    groups = group_similar_files(hashes, threshold)
    if not groups and mode != "matrix":
        print("No similar files found.")
    elif mode == "copy":
        print(f"Found {len(groups)} groups of similar files.")
        copy_groups(groups)
        print("Copied groups to 'output' directory.")
    elif mode in {"csv", "json"}:
        print(f"Found {len(groups)} groups of similar files.")
        write_report(groups, format=mode)
    elif mode == "matrix":
        write_matrix(hashes, threshold, pretty=True)
    else:
        print("Unknown mode. Use 'copy', 'csv', 'json', or 'matrix'.")


def safe_mkdir(base: Path) -> Path:
    if not base.exists():
        base.mkdir()
        return base
    i = 1
    while True:
        candidate = base.with_name(f"{base.name}_{i}")
        if not candidate.exists():
            candidate.mkdir()
            return candidate
        i += 1


def process_file(filepath):
    counter = Counter()
    try:
        with Path(filepath).open(encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line:
                    counter[line] += 1
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return counter


def collect_files_by_extension():
    ext_map = {}
    for root, _, filenames in os.walk(Path.cwd()):
        for fname in filenames:
            if fname.startswith("."):
                continue
            full_path = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower().lstrip(".")
            if ext in EXCLUDED_EXTENSIONS:
                continue
            if not ext:
                ext = "no_ext"
            ext_map.setdefault(ext, []).append(full_path)
    return ext_map


def main():
    ext_map = collect_files_by_extension()
    if not ext_map:
        print("No eligible files found.")
        return
    for ext, files in ext_map.items():
        collect_lines_for_extension(ext, files)


MAX_CHARS = 5000
MAX_CHARS = 5000


def clean_file(path: str) -> None:
    try:
        original = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    cleaned = clean_text(original)
    if cleaned != original:
        Path(path).write_text(cleaned, encoding="utf-8")


def get_mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _open_source(filepath: str):
    size = Path(filepath).stat().st_size
    f = Path(filepath).open("rb")
    if size > SIZE_THRESHOLD:
        return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    return f


def _read_text(filepath: str) -> str | None:
    try:
        with Path(filepath).open(encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def _has_rich_print_import(text: str) -> bool:
    return "from rich import print" in text


def regex_flag(filepath: str) -> bool:
    text = _read_text(filepath)
    if not text:
        return False
    if _has_rich_print_import(text):
        return False
    return bool(OLD_PRINT_RE.search(text))


def tokenizer_confirm(filepath: str) -> str | None:
    try:
        src = _open_source(filepath)
        tokens = list(tokenize.tokenize(src.readline))
    except Exception:
        return None
    for i, tok in enumerate(tokens):
        if tok.type == tokenize.NAME and tok.string == "print":
            line = tok.line.rstrip()
            if line.strip() == "print":
                continue
            j = i + 1
            while j < len(tokens) and tokens[j].type in {
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
            }:
                j += 1
            if j < len(tokens) and tokens[j].string != "(":
                return line
    return None


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


def fsz(sz: float) -> str:
    sz = abs(int(sz))
    units = ("", "K", "M", "G", "T")
    if sz == 0:
        return "0 B"
    i = min(int(int(sz).bit_length() - 1) // 10, len(units) - 1)
    sz /= 1024**i
    return f"{int(sz)} {units[i]}B"


def gsz(path: str | Path) -> int:
    path = Path(path)
    total_size = 0
    if not path.exists():
        return 0
    if path.is_file():
        try:
            total_size = path.stat().st_size
        except OSError:
            return 0
    elif path.is_dir():
        for entry in _scandir(path):
            try:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += gsz(entry.path)
            except OSError:
                continue
    return total_size


def gsz(path: str | Path) -> int:
    path = Path(path)
    total_size = 0
    if not path.exists():
        return 0
    if path.is_file():
        try:
            total_size = path.stat().st_size
        except OSError:
            return 0
    elif path.is_dir():
        for entry in _scandir(path):
            try:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += gsz(entry.path)
            except OSError:
                continue
    return total_size


def gsz(path: str | Path) -> int:
    path = Path(path)
    total_size = 0
    if not path.exists():
        return 0
    if path.is_file():
        try:
            total_size = path.stat().st_size
        except OSError:
            return 0
    elif path.is_dir():
        for entry in _scandir(path):
            try:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += gsz(entry.path)
            except OSError:
                continue
    return total_size


def count_lines_of_code(file_path, lang):
    if ".git" in str(file_path):
        return (0, 0, 0)
    if is_binary(file_path):
        print(f"{file_path} is binary")
        return (0, 0, 0)
    with Path(file_path).open(encoding="utf-8") as file:
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        for line in file:
            if not line.strip():
                blank_lines += 1
            elif re.match(COMMENT_PATTERNS.get(lang, ""), line):
                comment_lines += 1
            else:
                code_lines += 1
    return (code_lines, comment_lines, blank_lines)


def save_file(output_file, content):
    Path(output_file).write_text(content, encoding="utf-8")


def find_chunk_boundary(text, max_chars):
    if len(text) <= max_chars:
        return len(text)
    search_area = text[:max_chars]
    for delimiter in ["\n", "\r\n", ".  ", "!  ", "?  ", "; ", ", ", " "]:
        last_pos = search_area.rfind(delimiter)
        if last_pos > 0:
            return last_pos + len(delimiter)
    last_space = search_area.rfind(" ")
    if last_space > 0:
        return last_space + 1
    return max_chars


def chunk_text(text, max_chars):
    chunks = []
    pos = 0
    while pos < len(text):
        remaining = text[pos:]
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        chunk_end = find_chunk_boundary(remaining, max_chars)
        chunks.append(remaining[:chunk_end])
        pos += chunk_end
    return chunks


def translate_file(input_file, source_lang="auto"):
    print(f"[INFO] Reading file: {input_file}")
    content = load_file(input_file)
    content_length = len(content)
    print(f"[INFO] File size: {content_length} characters")
    if content_length <= MAX_CHARS:
        print(f"[INFO] Content fits in single request ({content_length} chars)")
        print("[INFO] Translating...")
        translated, detected_lang = translate_chunk(content, source_lang)
        print(f"[INFO] Detected language: {detected_lang}")
        return translated
    chunks = chunk_text(content, MAX_CHARS)
    total_chunks = len(chunks)
    print(f"[INFO] Content split into {total_chunks} chunks")
    print(f"[INFO] Chunk sizes: {[len(c) for c in chunks]}")
    translated_chunks = []
    detected_lang = None
    pbar = tqdm(total=total_chunks, desc="Translating", unit="chunk")
    try:
        for i, chunk in enumerate(chunks):
            print(f"\n[INFO] Translating chunk {i + 1}/{total_chunks} ({len(chunk)} chars)...")
            try:
                translated_chunk, detected_lang = translate_chunk(chunk, source_lang)
                translated_chunks.append(translated_chunk)
                pbar.update(1)
            except Exception as e:
                print(f"[ERROR] Failed to translate chunk {i + 1}: {e}")
                pbar.update(1)
                translated_chunks.append(chunk)
    finally:
        pbar.close()
    result = "".join(translated_chunks)
    print(f"\n[INFO] Detected language: {detected_lang}")
    return result


def is_english(text):
    return not non_english_pattern.search(text)


def find_site_packages() -> Path:
    return Path(sysconfig.get_paths()["purelib"])


def list_installed_packages(site: Path):
    pkgs = {}
    for item in site.iterdir():
        if item.name.endswith(".dist-info"):
            name_version = item.name[:-10]
            m = re.match("(.+)-([\\w\\.]+)", name_version)
            if not m:
                continue
            pkg, version = (m.group(1), m.group(2))
            pkgs[pkg.lower()] = (pkg, version)
    return pkgs


def get_wheel_tags(dist_info: Path):
    wheel_file = dist_info / "WHEEL"
    if not wheel_file.exists():
        return ["py3-none-any"]
    content = wheel_file.read_text()
    tags = [line.split(":", 1)[1].strip() for line in content.splitlines() if line.startswith("Tag:")]
    return tags or ["py3-none-any"]


def copy_package_files(pkg: str, site: Path, dst: Path) -> None:
    candidates = [
        site / pkg,
        site / f"{pkg}.py",
        site / f"{pkg.replace('-', '_')}",
        site / f"{pkg.replace('-', '_')}.py",
    ]
    for c in candidates:
        if c.exists():
            if c.is_dir():
                shutil.copytree(c, dst / c.name)
            else:
                shutil.copy2(c, dst / c.name)
            break


def copy_dist_info(pkg: str, version: str, site: Path, dst: Path) -> Path:
    dist_dir = site / f"{pkg}-{version}.dist-info"
    out = dst / dist_dir.name
    shutil.copytree(dist_dir, out)
    return out


def copy_scripts(pkg: str, dst: Path) -> None:
    scripts_dir = Path(sysconfig.get_paths()["scripts"])
    if not scripts_dir.exists():
        return
    pattern = re.compile(f"^{pkg}(-.+)?$")
    for script in scripts_dir.iterdir():
        if script.is_file() and pattern.match(script.name):
            shutil.copy2(script, dst / script.name)


def build_wheel(pkg: str, version: str, tag: str, src_dir: Path, out_dir: Path):
    wheel_name = f"{pkg}-{version}-{tag}.whl"
    wheel_path = out_dir / wheel_name
    with WheelFile(str(wheel_path), "w") as wf:
        for root, _dirs, files in os.walk(src_dir):
            for file in files:
                full = Path(root) / file
                arcname = full.relative_to(src_dir)
                wf.write(str(full), str(arcname))
    return wheel_path


def repack(pkg: str, site: Path, out_repack: Path, out_whl: Path) -> None:
    pkg_lower = pkg.lower()
    installed = list_installed_packages(site)
    if pkg_lower not in installed:
        print(f"Package '{pkg}' not found.")
        return
    real_pkg, version = installed[pkg_lower]
    target_dir = out_repack / real_pkg
    target_dir.mkdir(parents=True, exist_ok=True)
    copy_package_files(real_pkg, site, target_dir)
    dist_info = copy_dist_info(real_pkg, version, site, target_dir)
    copy_scripts(real_pkg, target_dir)
    tags = get_wheel_tags(dist_info)
    tag = tags[0]
    wheel = build_wheel(real_pkg, version, tag, target_dir, out_whl)
    print(f"Repacked: {real_pkg} → {wheel}")


def ensure_dirs():
    ERROR_DIR.mkdir(exist_ok=True)
    OK_DIR.mkdir(exist_ok=True)


def unique_destination(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    counter = 1
    while True:
        new_dest = parent / f"{stem}_{counter}{suffix}"
        if not new_dest.exists():
            return new_dest
        counter += 1


def get_installed_debian_packages() -> list[str]:
    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${binary:Package}\n"], check=True, capture_output=True, text=True
        )
    except FileNotFoundError:
        sys.exit("dpkg-query not found. Are you on a Debian-based system?")
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.stderr.strip())
    return sorted((pkg for pkg in result.stdout.splitlines() if pkg))


def save_packages(packages: list[str], path: Path) -> None:
    path.write_text("\n".join(packages) + "\n", encoding="utf-8")


def main() -> None:
    packages = get_installed_debian_packages()
    save_packages(packages, OUTPUT_FILE)
    print(f"Saved {len(packages)} packages to {OUTPUT_FILE.resolve()}")


def translate_chunk(chunk: str) -> str:
    try:
        return GoogleTranslator(source="auto", target="en").translate(chunk)
    except Exception as e:
        print(f"Chunk translation error: {e}")
        return chunk


def translate_file(path: Path):
    try:
        content = Path(path).read_text(encoding="utf-8")
    except:
        print(f"Skipping unreadable file: {path}")
        return
    if not non_english_pattern.search(content):
        return
    chunks = split_into_chunks(content, CHUNK_SIZE)
    with ThreadPoolExecutor(max_workers=8) as executor:
        translated_chunks = list(executor.map(translate_chunk, chunks))
    translated_text = "".join(translated_chunks)
    new_name = f"{path.stem}_eng{path.suffix}"
    new_path = path.parent / new_name
    try:
        Path(new_path).write_text(translated_text, encoding="utf-8")
        print(f"Translated → {new_path.name}")
    except Exception as e:
        print(f"Error writing {new_path}: {e}")


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


def write_text_file(path: Path, data: str) -> None:
    path.write_text(data, encoding="utf-8")


def write_text_file(path: Path, data: str) -> None:
    path.write_text(data, encoding="utf-8")


def build_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_eng{input_path.suffix}")


def build_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_eng{input_path.suffix}")


def is_text_file(file_path, text_extensions):
    return file_path.suffix.lower() in text_extensions


INPUT_FILE = "words.txt"
INPUT_FILE = "words.txt"
OUTPUT_FILE = "dic.json"


def translate_word(word):
    for attempt in range(3):
        try:
            return GoogleTranslator(source="auto", target="en").translate(word)
        except Exception as e:
            print(f"[WARN] Failed '{word}' (attempt {attempt + 1}): {e}")
            time.sleep(0.5)
    return None


def main():
    cwd = Path.cwd()
    args = sys.argv[1:]
    if args:
        files = [Path(p) for p in args]
        for path in files:
            process_file(path)
        sys.exit(0)
    for path in cwd.rglob("*.pdf"):
        process_file(path)


CHUNK_SIZE = 32768
CHUNK_SIZE = 32768
CHUNK_SIZE = 32768
CHUNK_SIZE = 32768
CHUNK_SIZE = 32768
LOG_EXT = ".log"


class ValidationError(Exception):
    pass


def should_preserve_comment(content):
    content = content.strip()
    return any((pat in content for pat in PRESERVED))


def find_docstring_ranges(node) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for child in ast.walk(node):
        if (
            isinstance(child, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and child.body
            and isinstance(child.body[0], ast.Expr)
        ):
            value = child.body[0].value
            if (
                isinstance(value, ast.Constant)
                and isinstance(value.value, str)
                and child.body[0].lineno
                and child.body[0].end_lineno
            ):
                ranges.append((child.body[0].lineno, child.body[0].end_lineno))
    return ranges


def find_docstring_ranges(node) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for child in ast.walk(node):
        if (
            isinstance(child, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and child.body
            and isinstance(child.body[0], ast.Expr)
        ):
            value = child.body[0].value
            if (
                isinstance(value, ast.Constant)
                and isinstance(value.value, str)
                and child.body[0].lineno
                and child.body[0].end_lineno
            ):
                ranges.append((child.body[0].lineno, child.body[0].end_lineno))
    return ranges


def to_ms(ts: str) -> int:
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)


def from_ms(ms: int) -> str:
    ms = max(ms, 0)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def extract_file(src: bytes, tree):
    root = tree.root_node
    return [src[node.start_byte : node.end_byte].decode() for node in root.children if node.type in VALID]


def extract_file(src: bytes, tree):
    root = tree.root_node
    return [src[node.start_byte : node.end_byte].decode() for node in root.children if node.type in VALID]


def extract_file(src: bytes, tree):
    root = tree.root_node
    return [src[node.start_byte : node.end_byte].decode() for node in root.children if node.type in VALID]


def extract_file(src: bytes, tree):
    root = tree.root_node
    return [src[node.start_byte : node.end_byte].decode() for node in root.children if node.type in VALID]


def extract_file(src: bytes, tree):
    root = tree.root_node
    return [src[node.start_byte : node.end_byte].decode() for node in root.children if node.type in VALID]


def get_dir_size(path):
    return sum((f.stat().st_size for f in path.rglob("*") if f.is_file()))


def extract_zst_file(archive_path, extract_path):
    output_path = extract_path / archive_path.stem
    with Path(archive_path).open("rb") as compressed_file:
        dctx = zstd.ZstdDecompressor()
        with Path(output_path).open("wb") as output_file:
            dctx.copy_stream(compressed_file, output_file)
    return output_path


def find_archives(directory):
    directory = Path(directory).resolve()
    archives = [zst_file for zst_file in directory.rglob("*.zst") if not zst_file.name.endswith(".tar.zst")]
    archives.extend(directory.rglob("*.tar.zst"))
    archives.extend(directory.rglob("*.tar.xz"))
    return sorted(set(archives))


def get_node_text(src: bytes, node):
    return src[node.start_byte : node.end_byte].decode()


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    try:
        return file_path.relative_to(base_path)
    except ValueError:
        return file_path


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    try:
        return file_path.relative_to(base_path)
    except ValueError:
        return file_path


processed_files_count = 0
processed_files_count = 0
total_definitions = 0
N_JOBS = -1
N_JOBS = -1
N_JOBS = -1
N_JOBS = -1
N_JOBS = -1
N_JOBS = -1
N_JOBS = -1


def compress_chunk(data, quality=QUALITY):
    return brotlicffi.compress(data, quality=quality)


def fsz(size: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(size) < 1024.0:
            return f"{size:3.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PiB"


def fsz(size: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(size) < 1024.0:
            return f"{size:3.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PiB"


def get_dirs(directory: Path) -> list[Path]:
    return [p for p in directory.glob("*") if not p.is_symlink() and p.is_dir()]


def main() -> None:
    asyncio.run(main_async())


OUT_PREFIX = "group_"
QUERY_STRING = "\n(comment) @comment\n(block\n  . (expression_statement\n    (string)) @docstring)\n(module\n  . (expression_statement\n    (string)) @docstring)\n"
QUERY_STRING = "\n(comment) @comment\n(block\n  . (expression_statement\n    (string)) @docstring)\n(module\n  . (expression_statement\n    (string)) @docstring)\n"


def should_preserve_comment(content):
    content = content.strip()
    return any((content.startswith(p) for p in ["#!", "# type:", "# fmt:"]))


MAX_WORKERS = 4


def find_html_files(directory: Path, recursive: bool = True) -> list[Path]:
    if recursive:
        html_files = list(directory.rglob("*.html")) + list(directory.rglob("*.htm"))
    else:
        html_files = list(directory.glob("*.html")) + list(directory.glob("*.htm"))
    return sorted(html_files)


TIMEOUT = 10
MAX_WORKERS = 8


def get_all_dist_info_dirs():
    dist_info_dirs = []
    for site_dir in [*site.getsitepackages(), site.getusersitepackages()]:
        if Path(site_dir).exists():
            dist_info_dirs.extend(
                (os.path.join(site_dir, item) for item in os.listdir(site_dir) if item.endswith(".dist-info"))
            )
    return dist_info_dirs


def get_sha256(path: str | Path) -> str:
    path = Path(path)
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def find_png_files(directory):
    png_files = []
    for root, _, files in os.walk(directory):
        png_files.extend((os.path.join(root, file) for file in files if file.lower().endswith(".png")))
    return png_files


ts_remover = None


def read_requirements(filename):
    req_file = Path(filename)
    with Path(req_file).open(encoding="utf-8") as f:
        return [line.strip().replace("-", "_").lower() for line in f if line.strip() and (not line.startswith("#"))]


def safe_rename(src: Path, dest_dir: Path) -> Path:
    dest = dest_dir / src.name
    if not dest.exists():
        return dest
    stem, suffix = (dest.stem, dest.suffix)
    i = 1
    while True:
        new_name = f"{stem}_{i}{suffix}"
        dest = dest_dir / new_name
        if not dest.exists():
            return dest
        i += 1


def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def unique_path(path: Path | str) -> Path:
    path = Path(path)
    if not path.exists():
        return path
    parent = path.parent
    suffixes = path.suffixes
    if suffixes:
        first_suffix_index = path.name.find(suffixes[0])
        stem = path.name[:first_suffix_index]
        full_suffix = "".join(suffixes)
    else:
        stem = path.name
        full_suffix = ""
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{full_suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def unique_path(path: Path | str) -> Path:
    path = Path(path)
    if not path.exists():
        return path
    parent = path.parent
    suffixes = path.suffixes
    if suffixes:
        first_suffix_index = path.name.find(suffixes[0])
        stem = path.name[:first_suffix_index]
        full_suffix = "".join(suffixes)
    else:
        stem = path.name
        full_suffix = ""
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{full_suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def main():
    root_dir = Path.cwd()
    before = gsz(root_dir)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(root_dir, recursive=True)
    for f in files:
        process_file(f)
    diff_size = before - gsz(root_dir)
    print(f"{fsz(diff_size)}")


def is_git_repo(path: Path) -> bool:
    return (path / ".git").is_dir()


def gather_python_files(root: Path):
    return [p for p in root.rglob("*.py") if p.is_file()]


def worker(args):
    return process_file(*args)


def find_dist_info_dir(site_packages: Path, pkg_name: str) -> Path:
    candidates = list(site_packages.glob(f"{pkg_name}-*.dist-info"))
    if not candidates:
        norm = pkg_name.replace("-", "_")
        candidates = list(site_packages.glob(f"{norm}-*.dist-info"))
    if not candidates:
        msg = f"Could not find any dist-info directory for package '{pkg_name}' in {site_packages}"
        raise FileNotFoundError(msg)
    if len(candidates) > 1:
        logger.warning("Multiple dist-info directories found for '{}', using: {}", pkg_name, candidates[0])
    return candidates[0]


WHEELS_OUTPUT_DIR = None


def find_dist_info_dir(pkg_dir: Path) -> Path | None:
    candidates = [p for p in pkg_dir.iterdir() if p.is_dir() and p.name.endswith(".dist-info")]
    if not candidates:
        return None
    if len(candidates) > 1:
        print(
            f"Warning: Multiple .dist-info dirs found in {pkg_dir}, using the first: {candidates[0].name}",
            file=sys.stderr,
        )
    return candidates[0]


output_filename = "env_vars.txt"
