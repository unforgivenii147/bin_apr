#!/data/data/com.termux/files/usr/bin/python

import mmap
import sys
from pathlib import Path
from binaryornot import is_binary
import brotlicffi
from dh import cprint, fsz, get_files, gsz, mpf3
# from joblib import Parallel, delayed

CHUNK_SIZE = 524288
N_JOBS = -1


def compress_chunk(data, mode: int = 0):
    return brotlicffi.compress(data, mode=mode, quality=11)


def parallel_compress(in_path, out_path):
    mode = 0
    if not is_binary(in_path):
        mode = 1
    try:
        file_size = in_path.stat().st_size
        if not file_size:
            return False
        chunk_count = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
        with out_path.open("wb", buffering=1024 * 1024) as fout, in_path.open("rb") as fin:
            mm = mmap.mmap(fin.fileno(), length=0, access=mmap.ACCESS_READ)
            chunks = [mm[i * CHUNK_SIZE : min((i + 1) * CHUNK_SIZE, file_size)] for i in range(chunk_count)]
            #            compressed_chunks=mpf3(compress_chunk,chunks)
            #            compressed_chunks = Parallel(n_jobs=N_JOBS, backend="loky")(
            #                (delayed(compress_chunk)(chunk) for chunk in chunks)
            #            )
            for chunk in chunks:
                block = compress_chunk(chunk, mode)
                fout.write(len(block).to_bytes(4, "big"))
                fout.write(block)
            mm.close()
            return True
    except OSError:
        return False


0


def process_file(fp):
    if not fp.exists() or fp.suffix == ".br":
        return
    before = gsz(fp)
    if not before:
        return
    outfile = Path(str(fp) + ".br")
    if parallel_compress(fp, outfile):
        fp.unlink()
    elif outfile.exists():
        outfile.unlink()
    after = gsz(outfile)
    dsz = abs(before - after)
    ratio = dsz / before * 100
    cprint(f"{outfile.name}", "green", end=" | ")
    cprint(f"{fsz(dsz)} | {ratio:.2f}%", "cyan")
    del before, after, ratio
    return


def main():
    cwd = Path.cwd()
    before = gsz(cwd)
    args = sys.argv[1:]
    files = [Path(arg) for arg in args] if args else get_files(cwd)
    mpf3(process_file, files)
    diff_size = before - gsz(cwd)
    print(f"{fsz(diff_size)}")


if __name__ == "__main__":
    sys.exit(main())
