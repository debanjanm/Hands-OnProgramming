# File Utils And Archives — Notes

## What this covers
Everything around files beyond plain reading and writing: copying and deleting trees (`shutil`), temp files (`tempfile`), finding files (`glob`, `os.scandir`, `os.walk`), permissions, safe atomic saves, comparing folders (`filecmp`), zip/tar archives, compression modules, and in-memory files (`io`). See `04-File-Handling.py` and `05-Pathlib-Module.py` for the basics.

## Key points
- **`shutil.copyfile`** copies content only; **`copy`** adds permissions; **`copy2`** adds timestamps too (use it for backups). **`copytree(src, dst, ignore=..., dirs_exist_ok=True)`** copies a folder; **`move`**, **`rmtree`** (no undo!), **`which`**, **`disk_usage`**, **`get_terminal_size`**, **`make_archive` / `unpack_archive`** are the other handy helpers.
- **`tempfile`**: `TemporaryDirectory`, `NamedTemporaryFile(delete=...)`, `SpooledTemporaryFile` (RAM until `max_size`), `mkstemp`/`mkdtemp` (you clean up; created private: `0600` / `0700`). It makes unique, race-free names.
- **`glob.glob(pattern)`**: `*`, `?`, `[abc]`; `**` only with `recursive=True`. `iglob` is the lazy version. `fnmatch` matches plain strings, `glob` matches the disk.
- **`os.scandir`** gives `DirEntry` objects whose `is_file()`/`is_dir()` are usually free; `os.listdir` gives only names.
- **`os.walk`**: edit `dirnames[:]` **in place** to skip folders (and to control order).
- **`os.stat`** + the `stat` module: `S_ISDIR`, `S_IMODE`, `filemode`. **`os.chmod(path, 0o600)`** for secrets.
- **Atomic write** = write a temp file in the same folder, `fsync`, then `os.replace(tmp, final)`. Readers see the old file or the new one, never half.
- **`filecmp.cmp(a, b, shallow=False)`** compares bytes; **`filecmp.dircmp`** compares folders (`left_only`, `right_only`, `diff_files`, `subdirs`).
- **Locking**: `fcntl.flock(f, LOCK_EX | LOCK_NB)` (POSIX only, advisory) raises `BlockingIOError` if someone else holds it.
- **`zipfile`**: `write`, `writestr`, `namelist`, `infolist` (`ZipInfo`), `read`, `open`, `extractall`, `testzip`. **`tarfile`**: modes `"w:gz"`, `"r:*"`, `add`, `extractall(filter="data")`.
- **Compression**: `zlib` (raw DEFLATE + `crc32`), `gzip`, `bz2`, `lzma` — all have `compress`/`decompress` and `open`. Use `shutil.copyfileobj` to stream big files.
- **`io.StringIO` / `io.BytesIO`** = files in memory (tests, building a zip or CSV without touching disk).

## Gotchas (the part worth revising twice)
- **`copyfile` loses permissions and mtime; `copy` loses mtime** — only `copy2` keeps both. None of them are atomic.
- **`copytree` fails if the destination exists** unless `dirs_exist_ok=True`. `shutil.move` into an existing folder moves the source **inside** it.
- **`open(path, "w")` truncates first** — a crash mid-write left an empty file in the demo; `atomic_write` kept the original. `os.replace` works over an existing file on every OS (`os.rename` does not on Windows).
- **`glob` without `recursive=True` treats `**` like `*`** (one level only), skips hidden files, and returns arbitrary order — wrap in `sorted()`. It returns `[]` instead of raising.
- **`dirnames = [...]` does NOT prune `os.walk`** — only the in-place `dirnames[:] = [...]` does.
- **`filecmp.cmp` defaults to `shallow=True`**: same size + same mtime = "equal" without reading content (the demo was fooled). `dircmp` also ignores `__pycache__`, `.git` etc. by default (`filecmp.DEFAULT_IGNORES`).
- **ZIP-slip**: names like `../evil.txt` escape the folder if you do `os.path.join(dest, name)` yourself (the demo wrote outside `inner/`). Python's `extractall` cleans names, but validate **all** names first, then extract; also cap total size (zip bombs).
- **tar is riskier**: members can be symlinks, absolute paths or setuid files. On 3.12 always pass `filter="data"` (omitting it warns; 3.14 makes it the default). It raised `OutsideDestinationError` and stripped the setuid bit. Members before the bad one may already be extracted — dry-run `tarfile.data_filter` on all members first.
- **`ZipFile(..., "w")` defaults to `ZIP_STORED` (no compression)** — pass `compression=zipfile.ZIP_DEFLATED`. Zip does not restore permissions or ownership; tar does.
- **Random or already-compressed data does not shrink** (it grew ~1–13% in the table). Don't re-compress zip/jpg/mp4.
- **`gzip.open(path)` is binary by default** — use `"rt"`/`"wt"` (with `encoding=`) for text.
- **`StringIO`/`BytesIO`: after writing, the cursor is at the end** — `seek(0)` before `read()`, or use `getvalue()`.
- **`NamedTemporaryFile` on Windows** cannot be reopened by name while open — use `delete=False` or (3.12+) `delete_on_close=False`. Never use `mktemp()`.
- `os.access()` then `open()` is a race — just try the `open()` and catch `PermissionError`.

## When it matters
Backups and deployments (`copytree`, archives, verify with a hash), safely saving config/state files, cleaning build folders, log compression, handling user-uploaded zip/tar files, scripts that must not run twice (locks), and tests that need scratch files or in-memory files.

## One-line recap example
```python
import os, tempfile
def atomic_write(path, text):                      # write temp -> fsync -> rename: never a half-written file
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)))
    with os.fdopen(fd, "w") as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
```
