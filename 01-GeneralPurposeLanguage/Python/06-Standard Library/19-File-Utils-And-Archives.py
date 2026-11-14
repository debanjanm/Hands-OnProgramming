import os
import sys
import io
import stat
import glob
import shutil
import filecmp
import fnmatch
import hashlib
import tempfile
import zipfile
import tarfile
import gzip
import bz2
import lzma
import zlib
import random
import csv

# 01. File Utilities and Archives - Introduction
# ------------------------------------
# - Reading/writing ONE file is in 05-Python Advanced/04-File-Handling.py and
#   path objects are in 06-Standard Library/05-Pathlib-Module.py. This file is
#   everything AROUND files: copying trees, temp files, searching, atomic
#   saves, comparing folders, zip/tar archives and compression.
# - Every demo happens inside ONE temporary directory that is deleted at the end,
#   so running this file leaves nothing behind.

print("# 01. File Utilities and Archives - Introduction")
print("# ------------------------------------")

TMP = tempfile.TemporaryDirectory()
ROOT = TMP.name


def P(*parts):
    """Build a path inside the temp area."""
    return os.path.join(ROOT, *parts)


def rel(paths, base):
    """Make a sorted list of forward-slash relative paths (stable output on every OS)."""
    return sorted(os.path.relpath(p, base).replace(os.sep, "/") for p in paths)


def write(path, text="", binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", **({} if binary else {"encoding": "utf-8"})) as f:
        f.write(text)
    return path


def tree(base):
    """All files and folders under base, relative and sorted."""
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        for name in dirnames + filenames:
            out.append(os.path.join(dirpath, name))
    return rel(out, base)


# 02. A sample project tree (used by the next sections)
# ------------------------------------
print("\n# 02. Sample tree")
SRC = P("project")
write(P("project", "src", "app.py"), "print('app')\n" * 20)
write(P("project", "src", "utils.py"), "def helper():\n    return 42\n" * 10)
write(P("project", "src", "__pycache__", "app.cpython-312.pyc"), b"\x00\x01binary", binary=True)
write(P("project", "src", "pkg", "deep.py"), "VALUE = 1\n")
write(P("project", "docs", "readme.md"), "# Project\nSome docs.\n" * 5)
write(P("project", "docs", "img", "logo.png"), b"\x89PNG\r\n" + bytes(range(64)), binary=True)
write(P("project", "data", "a.csv"), "id,name\n1,Asha\n2,Ravi\n")
write(P("project", ".env"), "SECRET=abc\n")
print("\n".join("  " + t for t in tree(SRC)))

# 03. shutil - copyfile vs copy vs copy2 (what metadata survives?)
# ------------------------------------
# - copyfile(src, dst) : contents ONLY. dst must be a full FILE path.
# - copy(src, dst)     : contents + permission bits. dst may be a directory.
# - copy2(src, dst)    : like copy + timestamps (and other metadata where possible).
#   Use copy2 for backups; plain copy when "a fresh file" is fine.
print("\n# 03. shutil - copyfile / copy / copy2")
original = P("meta", "original.txt")
write(original, "hello metadata\n")
OLD_TIME = 1_577_836_800  # 2020-01-01 00:00:00 UTC, fixed so the demo is deterministic
os.utime(original, (OLD_TIME, OLD_TIME))
if os.name != "nt":
    os.chmod(original, 0o640)

shutil.copyfile(original, P("meta", "by_copyfile.txt"))
shutil.copy(original, P("meta", "by_copy.txt"))
shutil.copy2(original, P("meta", "by_copy2.txt"))
for name in ("by_copyfile.txt", "by_copy.txt", "by_copy2.txt"):
    st = os.stat(P("meta", name))
    same_time = int(st.st_mtime) == OLD_TIME
    mode_kept = str(stat.S_IMODE(st.st_mode) == 0o640) if os.name != "nt" else "n/a (Windows)"
    print(f"  {name:16} mtime kept: {str(same_time):5}  0o640 permissions kept: {mode_kept}")
os.makedirs(P("meta", "dest_dir"))
print("shutil.copy returns the new path:", rel([shutil.copy(original, P("meta", "dest_dir"))], ROOT))
try:
    shutil.copyfile(original, P("meta", "dest_dir"))  # copyfile needs a FILE path, not a directory
except (IsADirectoryError, PermissionError) as e:
    print("copyfile into a directory ->", type(e).__name__)
print("# Gotcha: nothing here is atomic - a crash mid-copy leaves a half-written file (see #13).")

# 04. shutil - copytree, move, rmtree
# ------------------------------------
# - copytree(src, dst, ignore=..., dirs_exist_ok=False): copy a whole folder.
#   By default dst must NOT exist; dirs_exist_ok=True (3.8+) merges into it.
# - ignore=shutil.ignore_patterns("*.pyc", "__pycache__") skips unwanted files.
# - move(src, dst): rename if on the same disk, otherwise copy + delete.
# - rmtree(path): delete a folder and EVERYTHING in it - no trash, no undo.
print("\n# 04. shutil - copytree, move, rmtree")
COPY = P("project_copy")
shutil.copytree(SRC, COPY, ignore=shutil.ignore_patterns("*.pyc", "__pycache__"))
print("copytree (ignoring pycache):")
print("\n".join("  " + t for t in tree(COPY)))
try:
    shutil.copytree(SRC, COPY)
except FileExistsError:
    print("copytree onto an existing folder -> FileExistsError (default)")
write(P("project", "src", "new_file.py"), "# added later\n")
shutil.copytree(SRC, COPY, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
print("dirs_exist_ok=True merged the new file:", os.path.exists(os.path.join(COPY, "src", "new_file.py")))

shutil.move(COPY, P("project_moved"))
print("after move: old exists =", os.path.exists(COPY), "| new exists =", os.path.exists(P("project_moved")))
os.makedirs(P("inbox"))
shutil.move(P("project_moved"), P("inbox"))  # destination is an existing dir -> moved INSIDE it
print("move into an existing dir lands inside:", os.path.isdir(P("inbox", "project_moved")))

shutil.rmtree(P("inbox"))
print("rmtree removed it:", not os.path.exists(P("inbox")))
try:
    shutil.rmtree(P("does_not_exist"))
except FileNotFoundError:
    print("rmtree on a missing folder -> FileNotFoundError")
shutil.rmtree(P("does_not_exist"), ignore_errors=True)  # quiet version
print("ignore_errors=True stays quiet (but hides REAL problems too, use sparingly)")
if sys.version_info >= (3, 12):
    problems = []
    shutil.rmtree(P("does_not_exist"), onexc=lambda func, path, exc: problems.append(type(exc).__name__))
    print("onexc handler (3.12+) saw:", problems, "(replaces the deprecated onerror)")
else:
    print("skipped: rmtree(onexc=...) needs 3.12+ (older versions use onerror)")

# 05. shutil - which, disk_usage, get_terminal_size
# ------------------------------------
print("\n# 05. shutil - which, disk_usage, get_terminal_size")
print("which('python3') found      :", shutil.which("python3") is not None, "(returns the full path, or None)")
print("which('no-such-tool-xyz')   :", shutil.which("no-such-tool-xyz"))
usage = shutil.disk_usage(ROOT)
print("disk_usage fields           :", usage._fields, "| used+free <= total:", usage.used + usage.free <= usage.total)
print("free space is reported in bytes ->", usage.free > 0, "(check it before writing something huge)")
size = shutil.get_terminal_size(fallback=(80, 24))
print("get_terminal_size           :", type(size).__name__, "columns >= 1:", size.columns >= 1, "(fallback used when not a TTY)")
print("which() tip: check a tool exists BEFORE calling subprocess, instead of catching FileNotFoundError.")

# 06. shutil - make_archive and unpack_archive
# ------------------------------------
# - One-liners to zip/tar a whole folder and to unpack. Good for quick jobs; for
#   control (compression level, filters, security checks) use zipfile/tarfile.
# - make_archive(base_name, format, root_dir): base_name has NO extension - it
#   is added for you ("zip", "tar", "gztar", "bztar", "xztar").
print("\n# 06. shutil.make_archive / unpack_archive")
archive = shutil.make_archive(P("quick_backup"), "zip", root_dir=SRC)
print("created           :", os.path.basename(archive))
print("supported formats :", [name for name, _ in shutil.get_archive_formats()])
shutil.unpack_archive(archive, P("quick_restore"))
print("unpacked files    :", [t for t in tree(P("quick_restore")) if "." in os.path.basename(t)])
print("# Gotcha: unpack_archive trusts the archive. For untrusted input see the safe extract helpers below (#17, #18).")

# 07. tempfile - the safe way to make scratch files
# ------------------------------------
# - NEVER invent names like "/tmp/myapp.tmp" - another program (or attacker) can
#   pre-create it. tempfile creates a UNIQUE name and opens it atomically.
# - TemporaryDirectory()        : folder, deleted (with contents) when the block ends
# - NamedTemporaryFile()        : file with a real name, deleted on close
# - TemporaryFile()             : file with no visible name (POSIX), always private
# - SpooledTemporaryFile        : stays in RAM until it grows past max_size
# - mkstemp() / mkdtemp()       : low-level; YOU must clean up. Created private (0600 / 0700).
print("\n# 07. tempfile in depth")
with tempfile.TemporaryDirectory(prefix="demo_", suffix="_dir") as td:
    print("TemporaryDirectory prefix/suffix ok:", os.path.basename(td).startswith("demo_") and td.endswith("_dir"))
    write(os.path.join(td, "x.txt"), "x")
print("after the with-block the folder is gone:", not os.path.exists(td))

with tempfile.NamedTemporaryFile("w+", suffix=".txt", dir=ROOT) as tf:
    tf.write("scratch data")
    tf.flush()  # make sure it's on disk before another reader opens it by name
    with open(tf.name, encoding="utf-8") as again:
        print("NamedTemporaryFile re-read by name:", again.read(), "| suffix:", tf.name[-4:])
print("deleted on close:", not os.path.exists(tf.name))

tf2 = tempfile.NamedTemporaryFile("w", suffix=".log", dir=ROOT, delete=False)
tf2.write("keep me")
tf2.close()
print("delete=False keeps it after close:", os.path.exists(tf2.name), "(you must os.remove it yourself)")
os.remove(tf2.name)
print("# Windows note: a file opened by NamedTemporaryFile(delete=True) usually CANNOT be opened a second time")
print("#   by name while still open. Workarounds: delete=False + manual remove, or on 3.12+ delete_on_close=False.")
if sys.version_info >= (3, 12):
    with tempfile.NamedTemporaryFile("w", dir=ROOT, delete_on_close=False) as tf3:
        tf3.write("data")
        tf3.close()  # closed, but NOT yet deleted -> safe to reopen by name (also on Windows)
        with open(tf3.name, encoding="utf-8") as again:
            print("delete_on_close=False (3.12+): reopened after close ->", again.read())
    print("   ...and removed when the with-block exited:", not os.path.exists(tf3.name))
else:
    print("skipped: delete_on_close needs Python 3.12+")

fd, tmp_name = tempfile.mkstemp(suffix=".bin", dir=ROOT)  # returns an OPEN file descriptor + the path
os.write(fd, b"raw bytes")
os.close(fd)  # forgetting this leaks a file descriptor
if os.name != "nt":
    print("mkstemp permissions:", oct(stat.S_IMODE(os.stat(tmp_name).st_mode)), "(owner-only)")
os.remove(tmp_name)
d = tempfile.mkdtemp(dir=ROOT)
if os.name != "nt":
    print("mkdtemp permissions:", oct(stat.S_IMODE(os.stat(d).st_mode)))
os.rmdir(d)
print("# Never use tempfile.mktemp(): it returns a name only (race condition) and is deprecated.")

with tempfile.SpooledTemporaryFile(max_size=50, mode="w+") as sp:
    sp.write("short")
    print("spooled, small -> rolled to disk?", sp._rolled, " (_rolled is a private attribute, shown for teaching only)")
    sp.write("x" * 100)  # passes max_size
    print("spooled, grown  -> rolled to disk now:", sp._rolled)
    sp.seek(0)
    print("content is the same either way, length:", len(sp.read()))

# 08. glob - find files by wildcard pattern
# ------------------------------------
# - glob.glob(pattern) -> list of real paths on disk that match.
#     *  any chars (not "/")  | ?  one char | [abc] set | **  any depth (needs recursive=True)
# - glob.iglob(...)       -> same but lazy (iterator) for huge trees.
# - Results come back in ARBITRARY order -> wrap in sorted() for stable output.
# - Hidden files (leading ".") are NOT matched by * unless you ask (include_hidden, 3.11+).
# - glob.escape(name) neutralises special characters like [ ] * ? in a literal file name.
# - fnmatch (see 18-Text-Utilities.py) matches plain STRINGS; glob matches the DISK.
print("\n# 08. glob")
print("*.py in src         :", rel(glob.glob(os.path.join(SRC, "src", "*.py")), SRC))
print("** without flag      :", rel(glob.glob(os.path.join(SRC, "**", "*.py")), SRC), "(** acts like * : one level only, deep.py missed)")
print("recursive=True      :", rel(glob.glob(os.path.join(SRC, "**", "*.py"), recursive=True), SRC), "(finds every depth)")
print("any file in docs/*  :", rel(glob.glob(os.path.join(SRC, "docs", "*")), SRC), "(img is a folder, listed too)")
print("hidden skipped by * :", rel(glob.glob(os.path.join(SRC, "*")), SRC))
if sys.version_info >= (3, 11):
    print("include_hidden=True :", rel(glob.glob(os.path.join(SRC, "*"), include_hidden=True), SRC))
else:
    print("skipped: include_hidden needs 3.11+. Workaround: also glob('.*') explicitly.")
print("explicit '.*'       :", rel(glob.glob(os.path.join(SRC, ".*")), SRC))
print("char class [ud]*.py :", rel(glob.glob(os.path.join(SRC, "src", "[ua]*.py")), SRC))
if sys.version_info >= (3, 10):
    print("root_dir= (3.10+)   :", sorted(glob.glob("**/*.csv", root_dir=SRC, recursive=True)), "<- results are relative to root_dir")
else:
    print("skipped: root_dir needs 3.10+")
print("iglob is lazy       :", type(glob.iglob(os.path.join(SRC, "*"))).__name__, "->", next(iter(glob.iglob(os.path.join(SRC, "docs", "*.md")))).endswith("readme.md"))
print("glob.escape         :", glob.escape("report[final]*.txt"))
print("# Gotcha: glob that matches nothing returns [] - it never raises, so check for empty.")

# 09. os.scandir vs os.listdir
# ------------------------------------
# - os.listdir(path) -> just NAMES. To know file-or-folder you need another
#   system call (os.path.isfile) for EVERY name.
# - os.scandir(path) -> DirEntry objects. is_file()/is_dir() usually come free
#   from the directory listing itself (no extra system call), so it is much
#   faster on big folders - and os.walk and pathlib use it internally.
# - Use it as a context manager so the directory handle is closed.
print("\n# 09. os.scandir vs os.listdir")
folder = os.path.join(SRC, "docs")
print("listdir (names only):", sorted(os.listdir(folder)))
with os.scandir(folder) as it:
    entries = sorted(it, key=lambda e: e.name)  # order is arbitrary, so sort
    for e in entries:
        kind = "dir " if e.is_dir() else "file"
        extra = f"size={e.stat().st_size}" if e.is_file() else ""
        print(f"  {kind} {e.name:12} {extra}")
print("DirEntry attributes: name, path, is_file(), is_dir(), is_symlink(), stat(), inode()")
print("is_file(follow_symlinks=False) lets you treat symlinks as their own thing (safer when scanning untrusted trees).")
print("# Rule of thumb: need only names -> listdir. Need file info too -> scandir.")

# 10. os.walk - walking a tree, pruning folders in place
# ------------------------------------
# - os.walk(top) yields (dirpath, dirnames, filenames) for each folder.
# - topdown=True (default) lets you EDIT dirnames IN PLACE to skip folders and
#   to control the order of traversal: dirnames[:] = [...]
# - GOTCHA: `dirnames = [...]` (rebinding) does nothing - walk keeps its own list.
# - os.walk silently ignores folders it cannot read unless you pass onerror=.
print("\n# 10. os.walk with pruning")
print("full walk, files only:")
all_files = []
for dirpath, dirnames, filenames in os.walk(SRC):
    dirnames.sort()  # makes traversal order deterministic
    all_files += [os.path.join(dirpath, f) for f in sorted(filenames)]
print("  ", rel(all_files, SRC))

SKIP = {"__pycache__", "img"}
pruned = []
for dirpath, dirnames, filenames in os.walk(SRC):
    dirnames[:] = sorted(d for d in dirnames if d not in SKIP)  # in-place slice assignment = prune
    pruned += [os.path.join(dirpath, f) for f in filenames]
print("pruned (no __pycache__ / img):")
print("  ", rel(pruned, SRC))

wrong = []
for dirpath, dirnames, filenames in os.walk(SRC):
    dirnames = [d for d in dirnames if d not in SKIP]  # BUG: rebinding does not prune
    wrong += [os.path.join(dirpath, f) for f in filenames]
print("rebinding bug still visits skipped dirs:", any("__pycache__" in w for w in wrong))

# 11. os.stat, st_mode and the stat module
# ------------------------------------
# - os.stat(path) returns size, times and a MODE number that packs file type
#   AND permission bits together.
# - stat.S_ISDIR(mode)/S_ISREG(mode)/S_ISLNK(mode) decode the type;
#   stat.S_IMODE(mode) keeps only the permission bits; stat.filemode(mode)
#   gives the "ls -l" style string.
# - Times are floats (seconds since 1970): st_mtime (modified), st_atime, st_ctime.
print("\n# 11. os.stat and the stat module")
target = os.path.join(SRC, "src", "app.py")
st = os.stat(target)
print("size in bytes :", st.st_size)
print("is regular file:", stat.S_ISREG(st.st_mode), "| is dir:", stat.S_ISDIR(st.st_mode))
print("dir check     :", stat.S_ISDIR(os.stat(SRC).st_mode))
print("mtime is a float:", isinstance(st.st_mtime, float))
print("os.path.getsize equals st_size:", os.path.getsize(target) == st.st_size)
print("# lstat() looks at a symlink itself, stat() follows it to the target.")

# 12. Permissions - chmod
# ------------------------------------
# - chmod(path, 0o640): owner read+write, group read, others nothing.
#   Octal digits are owner/group/others; 4=read 2=write 1=execute.
# - Secrets (keys, tokens, .env) should be 0o600. Scripts need the x bit.
# - On Windows chmod only toggles read-only, so guard it.
print("\n# 12. chmod")
if os.name != "nt":
    secret = P("keys", "api.key")
    write(secret, "token")
    os.chmod(secret, 0o600)
    m = os.stat(secret).st_mode
    print("0o600 ->", stat.filemode(m), oct(stat.S_IMODE(m)))
    os.chmod(secret, m | stat.S_IXUSR)  # add owner-execute without touching the rest
    print("+x for owner ->", stat.filemode(os.stat(secret).st_mode))
    print("os.access(secret, os.R_OK):", os.access(secret, os.R_OK), "| W_OK:", os.access(secret, os.W_OK))
else:
    print("skipped: chmod permission bits are POSIX-only (Windows only has read-only)")
print("# Gotcha: os.access() then open() is a race (check-then-use). Just try open() and catch PermissionError.")

# 13. os.replace and atomic file writes
# ------------------------------------
# - Problem: open(path, "w") TRUNCATES the file first. If the program crashes (or
#   the disk fills) while writing, the old content is gone and the new content
#   is incomplete.
# - Fix ("write temp, then rename"):
#     1. write the new content to a temp file IN THE SAME FOLDER
#     2. flush + fsync so it is really on disk
#     3. os.replace(temp, final): atomic - readers see old OR new, never half.
# - os.replace overwrites on every OS (os.rename fails on Windows if dst exists).
# - Must be the same filesystem, which is why the temp file lives beside the target.
print("\n# 13. Atomic writes with os.replace")


def atomic_write(path, data):
    """Replace `path` with `data` (str or bytes) so a failure can never leave a half-written file."""
    path = os.path.abspath(path)
    directory = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".part")
    try:
        mode = "wb" if isinstance(data, (bytes, bytearray)) else "w"
        with os.fdopen(fd, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())  # force the bytes to disk before the rename
        if os.path.exists(path):
            shutil.copymode(path, tmp_path)  # mkstemp makes 0600; keep the original's permissions
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)  # never leave the temp file behind
        except FileNotFoundError:
            pass
        raise


config = P("conf", "settings.ini")
write(config, "mode=safe\n")
atomic_write(config, "mode=fast\nretries=3\n")
with open(config, encoding="utf-8") as f:
    print("after atomic_write:", repr(f.read()))
print("leftover temp files :", [n for n in os.listdir(os.path.dirname(config)) if n.startswith(".tmp-")])

# Simulate a failure DURING the write by handing over data that cannot be written.
naive_target = P("conf", "naive.ini")
write(naive_target, "important=1\n")
try:
    with open(naive_target, "w", encoding="utf-8") as f:  # truncates immediately!
        f.write(object())  # TypeError, like a crash half way
except TypeError:
    pass
print("naive open('w') after failure :", repr(open(naive_target, encoding="utf-8").read()), "<- data LOST")

safe_target = P("conf", "safe.ini")
write(safe_target, "important=1\n")
try:
    atomic_write(safe_target, object())
except TypeError:
    pass
print("atomic_write after failure    :", repr(open(safe_target, encoding="utf-8").read()), "<- original intact")
print("leftover temp files           :", [n for n in os.listdir(os.path.dirname(safe_target)) if n.startswith(".tmp-")])
print("# Used for: config files, caches, JSON state files, anything another process might read at any moment.")

# 14. filecmp - compare files and folders
# ------------------------------------
# - filecmp.cmp(a, b, shallow=True): True if the files are "the same".
#   GOTCHA: shallow=True only compares os.stat() signatures (type, size, mtime)
#   and says "same" if those match WITHOUT reading the content!
#   Use shallow=False when you care about the actual bytes.
# - filecmp.dircmp(a, b): compare two folders: left_only, right_only, common,
#   diff_files, funny_files, and subdirs for recursion.
# - dircmp ignores names in filecmp.DEFAULT_IGNORES (e.g. __pycache__, .git) by default!
print("\n# 14. filecmp")
fa, fb, fc = P("cmp", "a.txt"), P("cmp", "b.txt"), P("cmp", "c.txt")
write(fa, "AAAA")
write(fb, "AAAA")
write(fc, "BBBB")  # same size as a.txt, different content
print("same content            :", filecmp.cmp(fa, fb, shallow=False))
print("different content       :", filecmp.cmp(fa, fc, shallow=False))
os.utime(fc, (os.stat(fa).st_atime, os.stat(fa).st_mtime))  # copy a.txt's timestamp onto c.txt
print("shallow=True (fooled!)  :", filecmp.cmp(fa, fc, shallow=True), "<- same size + same mtime, content NOT read")
print("shallow=False (truth)   :", filecmp.cmp(fa, fc, shallow=False))

left, right = P("dc", "left"), P("dc", "right")
for base in (left, right):
    write(os.path.join(base, "same.txt"), "same")
    write(os.path.join(base, "sub", "deep.txt"), "deep")
write(os.path.join(left, "changed.txt"), "version 1")
write(os.path.join(right, "changed.txt"), "version 2!")
write(os.path.join(left, "only_left.txt"), "L")
write(os.path.join(right, "only_right.txt"), "R")
dc = filecmp.dircmp(left, right)
print("left_only  :", sorted(dc.left_only))
print("right_only :", sorted(dc.right_only))
print("common     :", sorted(dc.common))
print("diff_files :", sorted(dc.diff_files))
print("subdirs    :", sorted(dc.subdirs), "-> dc.subdirs['sub'].diff_files =", dc.subdirs["sub"].diff_files)
print("DEFAULT_IGNORES:", filecmp.DEFAULT_IGNORES)


def same_tree(a, b, ignore=()):
    """True only if both folders have identical files and content (recursive, content-based)."""
    cmp = filecmp.dircmp(a, b, ignore=list(filecmp.DEFAULT_IGNORES) + list(ignore))
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    if mismatch or errors:
        return False
    return all(same_tree(os.path.join(a, d), os.path.join(b, d), ignore) for d in cmp.common_dirs)


print("same_tree(left, right)  :", same_tree(left, right))
print("same_tree(left, left)   :", same_tree(left, left))

# 15. File locking (brief reference)
# ------------------------------------
# - Two processes writing the same file can corrupt it. A lock makes them take turns.
# - Locks are ADVISORY: they only work if every program politely asks for them.
# - POSIX: fcntl.flock / fcntl.lockf.   Windows: msvcrt.locking.
#   Portable and easier: the third-party `filelock` package.
# - LOCK_EX = exclusive, LOCK_NB = don't wait - raise BlockingIOError instead.
print("\n# 15. File locking (fcntl, POSIX only)")
try:
    import fcntl
except ImportError:
    fcntl = None
    print("skipped: fcntl is not available on this platform (Windows -> msvcrt.locking or `filelock`)")
if fcntl:
    lock_path = P("locks", "job.lock")
    os.makedirs(os.path.dirname(lock_path))
    first = open(lock_path, "w")
    second = open(lock_path, "w")
    fcntl.flock(first, fcntl.LOCK_EX)
    print("first handle holds the lock")
    try:
        fcntl.flock(second, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print("second handle got it (unexpected)")
    except BlockingIOError:
        print("second handle -> BlockingIOError: someone else is running (use this to stop duplicate cron jobs)")
    fcntl.flock(first, fcntl.LOCK_UN)
    fcntl.flock(second, fcntl.LOCK_EX | fcntl.LOCK_NB)
    print("after unlock, second handle acquires it")
    first.close()
    second.close()  # closing also releases a lock

# 16. zipfile - reading and writing .zip archives
# ------------------------------------
# - ZipFile(path, mode): "w" create/overwrite, "r" read, "a" append.
# - Compression is a CHOICE: ZIP_STORED (none, default!), ZIP_DEFLATED (the usual),
#   ZIP_BZIP2, ZIP_LZMA. Forgetting compression= gives an uncompressed zip.
# - write(file, arcname=...) adds a file from disk; writestr(name, data) adds data from memory.
# - namelist(), infolist() -> ZipInfo (filename, file_size, compress_size, CRC, date_time).
# - read(name) -> bytes; open(name) -> stream; extract / extractall -> to disk.
# - testzip() returns the first corrupt member, or None if the archive is fine.
print("\n# 16. zipfile")
zpath = P("demo.zip")
FIXED = (2024, 1, 1, 0, 0, 0)  # fixed timestamps -> reproducible archives
with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(SRC, "src", "app.py"), arcname="code/app.py")  # arcname controls the path INSIDE the zip
    zf.writestr("notes/hello.txt", "hello zip\n" * 50)
    info = zipfile.ZipInfo("notes/fixed_time.txt", date_time=FIXED)
    info.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(info, "reproducible entry")
print("is_zipfile :", zipfile.is_zipfile(zpath), "| not a zip:", zipfile.is_zipfile(os.path.join(SRC, ".env")))
with zipfile.ZipFile(zpath) as zf:
    print("namelist   :", zf.namelist())
    for zi in zf.infolist():
        print(f"  {zi.filename:22} size={zi.file_size:5} packed={zi.compress_size:5} method={zi.compress_type} (8 = deflate)")
    print("ZipInfo.date_time of the fixed entry:", zf.getinfo("notes/fixed_time.txt").date_time)
    print("read()     :", zf.read("notes/fixed_time.txt"))
    with zf.open("notes/hello.txt") as member:  # stream: no need to load a huge member into memory
        print("open() first line:", member.readline())
    print("testzip()  :", zf.testzip(), "(None = every CRC matches)")
    if sys.version_info >= (3, 8):
        print("zipfile.Path:", sorted(p.name for p in zipfile.Path(zf, "notes/").iterdir()))
    zf.extractall(P("unzipped"))
print("extractall ->", tree(P("unzipped")))

print("compression methods on the same text:")
body = ("the quick brown fox jumps over the lazy dog\n" * 400).encode()
for label, method in [("ZIP_STORED", zipfile.ZIP_STORED), ("ZIP_DEFLATED", zipfile.ZIP_DEFLATED),
                      ("ZIP_BZIP2", zipfile.ZIP_BZIP2), ("ZIP_LZMA", zipfile.ZIP_LZMA)]:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=method) as zf:
        zf.writestr("t.txt", body)
    print(f"  {label:13} {len(body)} -> {len(buf.getvalue()):6} bytes")
print("# Gotchas: passwords - zipfile can only READ legacy (weak) encryption via setpassword(); it cannot write it.")
print("#          writing the same name twice makes a duplicate entry (UserWarning) - last one wins on extract.")

# 17. ZIP-slip: why you must not trust archive member names
# ------------------------------------
# - ZIP-slip = a malicious archive contains names like "../../etc/cron.d/x" or
#   "/home/user/.bashrc". Code that does os.path.join(dest, name) then writes
#   there ESCAPES the extraction folder and overwrites any file you can write.
# - Python's own extract()/extractall() clean such names (they strip ".." and
#   drive/leading "/"), but hand-written extraction code, and other tools, do not.
#   Defence in depth: validate every name yourself, and check ALL names BEFORE
#   writing ANY file (all or nothing). Also cap the total size (zip bombs).
print("\n# 17. ZIP-slip and a safe extract helper")
evil_zip = P("evil.zip")
with zipfile.ZipFile(evil_zip, "w") as zf:
    zf.writestr("ok/fine.txt", "harmless")
    zf.writestr("../evil.txt", "pwned")  # tries to climb out of the destination
    zf.writestr("/absolute_evil.txt", "pwned too")  # tries an absolute path

NAIVE_DEST = P("naive_dest", "inner")
os.makedirs(NAIVE_DEST)
with zipfile.ZipFile(evil_zip) as zf:  # NAIVE extraction, only for ../ and kept inside our temp area
    name = "../evil.txt"
    out_path = os.path.join(NAIVE_DEST, name)
    with open(out_path, "wb") as f:
        f.write(zf.read(name))
print("naive join wrote to      :", os.path.relpath(os.path.normpath(out_path), ROOT), "<- OUTSIDE 'inner'!")
print("escaped the folder       :", os.path.exists(P("naive_dest", "evil.txt")))

with zipfile.ZipFile(evil_zip) as zf:  # Python's built-in cleaning
    zf.extractall(P("builtin_dest"))
print("zipfile.extractall result:", tree(P("builtin_dest")), "<- names were sanitised")


def safe_extract_zip(zf, dest, max_total_bytes=50 * 1024 * 1024):
    """Extract zf into dest, refusing anything that would land outside it. Validates everything first."""
    dest_real = os.path.realpath(dest)
    if sum(i.file_size for i in zf.infolist()) > max_total_bytes:
        raise ValueError("archive is too large when unpacked (possible zip bomb)")
    for info in zf.infolist():
        target = os.path.realpath(os.path.join(dest_real, info.filename))
        try:
            inside = os.path.commonpath([dest_real, target]) == dest_real
        except ValueError:  # e.g. different drives on Windows
            inside = False
        if not inside:
            raise ValueError(f"unsafe path in archive: {info.filename!r}")
    zf.extractall(dest_real)


with zipfile.ZipFile(evil_zip) as zf:
    try:
        safe_extract_zip(zf, P("safe_dest"))
    except ValueError as e:
        print("safe_extract_zip rejected:", e)
print("nothing was written       :", not os.path.exists(P("safe_dest")) or tree(P("safe_dest")) == [])
with zipfile.ZipFile(zpath) as zf:
    safe_extract_zip(zf, P("safe_ok"))
print("a normal zip extracts fine:", tree(P("safe_ok")))

# 18. tarfile - the Unix archive format
# ------------------------------------
# - tar bundles files (keeping permissions, owners, symlinks); compression is
#   added on top: modes "w", "w:gz", "w:bz2", "w:xz" (.tar.gz = "tgz").
# - Reading: mode "r:*" (or just "r") detects the compression automatically.
# - add(path, arcname=..., filter=fn) lets you edit or drop members as they are added.
# - SECURITY CHANGE: tar members can be symlinks, devices, absolute paths, files with
#   setuid bits... Extracting an untrusted tar used to be dangerous by default.
#   Python 3.12 added extraction FILTERS (also backported to security releases):
#       filter="fully_trusted" : old behaviour, trust everything
#       filter="tar"           : block absolute paths and ".." only
#       filter="data"          : strict. No links outside the folder, no special
#                                files, no setuid, sane permissions. Use this.
#   In 3.12 omitting filter= raises a DeprecationWarning; in 3.14 'data' is the default.
print("\n# 18. tarfile")
tpath = P("project.tar.gz")


def strip_owner(ti):
    ti.uid = ti.gid = 0  # don't leak the local user ids into the archive
    ti.uname = ti.gname = ""
    ti.mtime = OLD_TIME  # fixed time -> reproducible
    return ti


with tarfile.open(tpath, "w:gz") as tar:
    tar.add(SRC, arcname="project", filter=lambda ti: None if "__pycache__" in ti.name else strip_owner(ti))
with tarfile.open(tpath, "r:*") as tar:
    names = tar.getnames()
    print("members       :", sorted(names))
    first_file = next(m for m in tar.getmembers() if m.name.endswith("data/a.csv"))
    print("member info   :", first_file.name, first_file.size, "bytes, is file:", first_file.isfile())
    print("extractfile   :", tar.extractfile(first_file).read())

if hasattr(tarfile, "data_filter"):  # present in 3.12+ and in later security releases of older versions
    with tarfile.open(tpath, "r:gz") as tar:
        tar.extractall(P("untarred"), filter="data")
    print("extractall(filter='data') ->", [t for t in tree(P("untarred")) if t.count("/") == 1][:3], "...")

    # Build a hostile tar in memory: one ../ escape and one setuid file.
    hostile = io.BytesIO()
    with tarfile.open(fileobj=hostile, mode="w") as tar:
        ok = tarfile.TarInfo("good.txt")
        payload = b"fine"
        ok.size = len(payload)
        tar.addfile(ok, io.BytesIO(payload))
        bad = tarfile.TarInfo("../escape.txt")
        bad.size = len(payload)
        tar.addfile(bad, io.BytesIO(payload))
    hostile.seek(0)
    os.makedirs(P("tar_dest", "inner"))
    with tarfile.open(fileobj=hostile) as tar:
        try:
            tar.extractall(P("tar_dest", "inner"), filter="data")
        except tarfile.FilterError as e:
            print("data filter blocked it ->", type(e).__name__, "for member", repr(e.tarinfo.name))
    print("escape.txt written outside?   :", os.path.exists(P("tar_dest", "escape.txt")))
    print("# Note: good.txt (listed BEFORE the bad member) may already be extracted - validate first for all-or-nothing:")
    hostile.seek(0)
    with tarfile.open(fileobj=hostile) as tar:
        try:
            [tarfile.data_filter(m, P("tar_dest", "inner")) for m in tar.getmembers()]  # dry run
        except tarfile.FilterError:
            print("   dry-run validation failed -> do not extract this archive at all")

    suid = tarfile.TarInfo("run.sh")
    suid.mode = 0o4755  # setuid + rwxr-xr-x
    cleaned = tarfile.data_filter(suid, ROOT)
    print("data_filter permissions   :", oct(suid.mode), "->", oct(cleaned.mode), "(setuid bit removed)")
else:
    print("skipped: tarfile extraction filters need Python 3.12+ (or a recent security release).")
    print("         On older versions only extract tar files you created yourself.")

# 19. Compression modules - gzip, bz2, lzma, zlib
# ------------------------------------
# - zlib : the engine (DEFLATE). Raw bytes in, raw bytes out. Also crc32/adler32 checksums.
# - gzip : zlib + a small header; the .gz file format (use for single files / HTTP).
# - bz2  : slower, usually smaller.   lzma : slowest, usually smallest (.xz / .lzma).
# - All four share the same shape: compress(bytes) / decompress(bytes), and
#   open(path, mode) for file streams. Compression does NOT combine files - that is
#   tar/zip's job (hence .tar.gz).
print("\n# 19. gzip / bz2 / lzma / zlib")
text_blob = ("2024-05-01 INFO user=asha action=login ok\n" * 600 + "2024-05-01 WARN disk=91%\n" * 100).encode()
rng = random.Random(7)
random_blob = bytes(rng.randrange(256) for _ in range(len(text_blob) // 8))
print("Ratio table (smaller % = better compression; sizes depend slightly on the zlib/xz version):")
print(f"  {'algorithm':<12}{'repetitive text':>22}{'random bytes':>22}")
print(f"  {'original':<12}{len(text_blob):>16} bytes{len(random_blob):>16} bytes")
for label, fn in [
    ("zlib -1", lambda b: zlib.compress(b, 1)),
    ("zlib -9", lambda b: zlib.compress(b, 9)),
    ("gzip", lambda b: gzip.compress(b, mtime=0)),
    ("bz2", bz2.compress),
    ("lzma", lzma.compress),
]:
    t, r = fn(text_blob), fn(random_blob)
    print(f"  {label:<12}{len(t):>9} ({len(t) / len(text_blob):>6.1%}){len(r):>10} ({len(r) / len(random_blob):>6.1%})")
print("# Random (already-compressed-like) data does not shrink - it can even GROW. Don't recompress zip/jpg/mp4/png.")
assert gzip.decompress(gzip.compress(text_blob)) == text_blob
assert lzma.decompress(lzma.compress(text_blob)) == text_blob
print("round trip decompress == original: True")
print("checksums     : crc32 =", zlib.crc32(b"hello"), "| adler32 =", zlib.adler32(b"hello"))

# Streaming: compress a big file without loading it all into memory.
big = P("stream", "big.log")
write(big, "some log line that repeats\n" * 5000)
with open(big, "rb") as src, gzip.open(big + ".gz", "wb") as dst:
    shutil.copyfileobj(src, dst)  # copies in chunks
print("streamed gzip :", os.path.getsize(big), "->", os.path.getsize(big + ".gz"), "bytes")

# gzip.open in TEXT mode ("wt"/"rt") with an encoding, just like open()
with gzip.open(P("stream", "notes.txt.gz"), "wt", encoding="utf-8") as f:
    f.write("café 日本語\nsecond line\n")
with gzip.open(P("stream", "notes.txt.gz"), "rt", encoding="utf-8") as f:
    for line in f:
        print("gzip text mode:", line.rstrip())
print("# Gotcha: gzip.open(path) defaults to BINARY ('rb'); you need 'rt' to get str.")

# Incremental compression of data that arrives in pieces (network streams, generators)
comp = zlib.compressobj(level=6)
chunks = [comp.compress(("chunk %d " % i).encode() * 50) for i in range(5)] + [comp.flush()]
packed = b"".join(chunks)
decomp = zlib.decompressobj()
restored = decomp.decompress(packed)
print("compressobj in 5 pieces:", len(restored), "bytes restored, matches:", restored == b"".join(("chunk %d " % i).encode() * 50 for i in range(5)))

# 20. io.StringIO and io.BytesIO - files that live in memory
# ------------------------------------
# - Many APIs want a "file-like object". StringIO (text) and BytesIO (bytes) give
#   you one without touching the disk. Perfect for tests, building a CSV/zip to
#   send over HTTP, and capturing output.
# - Gotcha: after writing, the cursor is at the END. seek(0) before reading.
# - getvalue() returns everything regardless of the cursor position.
print("\n# 20. io.StringIO and io.BytesIO")
sio = io.StringIO()
sio.write("line 1\n")
print("line 2", file=sio)  # print can target any file-like object
print("read right after writing :", repr(sio.read()), "<- empty, the cursor is at the end")
sio.seek(0)
print("after seek(0)            :", repr(sio.read()))
print("getvalue()               :", repr(sio.getvalue()))

csv_buf = io.StringIO(newline="")
csv.writer(csv_buf).writerows([["id", "name"], [1, "Asha"], [2, "O'Brien, Jr."]])
print("csv built in memory      :", repr(csv_buf.getvalue()))
print("read it back via csv     :", list(csv.reader(io.StringIO(csv_buf.getvalue()))))

bio = io.BytesIO()
with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as zf:  # a zip that never touches the disk
    zf.writestr("report.txt", "built in memory\n" * 10)
print("zip in BytesIO           :", len(bio.getvalue()), "bytes, starts with", bio.getvalue()[:2], "(PK = zip signature)")
with zipfile.ZipFile(io.BytesIO(bio.getvalue())) as zf:
    print("read it back             :", zf.namelist())


def count_lines(file_obj):
    return sum(1 for _ in file_obj)


print("same function, real file and StringIO:", count_lines(open(big, encoding="utf-8")), count_lines(io.StringIO("a\nb\nc\n")))

# 21. Worked example - backup, verify, restore, compare
# ------------------------------------
# - Back up a folder into ONE zip with a fixed (timestamp-free) name:
#     1. collect the files (prune junk like __pycache__), sorted for stability
#     2. write them with ZIP_DEFLATED and forward-slash names
#     3. verify: testzip() + SHA-256 of every file against the original
#     4. restore with the SAFE extractor, then compare folders with filecmp
#   A timestamp-free name (backup.zip) means the latest backup overwrites the
#   previous one - add dates in the name only if you want history.
print("\n# 21. Worked example - backup, verify, restore, compare")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(64 * 1024), b""):  # chunked: any file size
            h.update(block)
    return h.hexdigest()


def backup_folder(src, zip_path, skip=("__pycache__",)):
    manifest = {}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = sorted(d for d in dirnames if d not in skip)
            for name in sorted(filenames):
                full = os.path.join(dirpath, name)
                arcname = os.path.relpath(full, src).replace(os.sep, "/")
                zf.write(full, arcname)
                manifest[arcname] = sha256_of(full)
    return manifest


def verify_backup(zip_path, manifest):
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        if bad:
            return f"corrupt member: {bad}"
        for arcname, digest in manifest.items():
            if hashlib.sha256(zf.read(arcname)).hexdigest() != digest:
                return f"hash mismatch: {arcname}"
    return "ok"


BACKUP = P("backups", "backup.zip")  # note: no timestamp in the name
os.makedirs(os.path.dirname(BACKUP))
manifest = backup_folder(SRC, BACKUP)
print("files backed up    :", sorted(manifest))
print("zip file hash      :", len(sha256_of(BACKUP)), "hex chars (keep it OUTSIDE the zip to detect later tampering of the zip itself)")
print("verify_backup      :", verify_backup(BACKUP, manifest))

RESTORED = P("restored")
with zipfile.ZipFile(BACKUP) as zf:
    safe_extract_zip(zf, RESTORED)
print("restored tree      :", len(tree(RESTORED)), "entries")

cmp = filecmp.dircmp(SRC, RESTORED)
print("dircmp top level   : left_only =", sorted(cmp.left_only), "| right_only =", sorted(cmp.right_only), "| diff_files =", cmp.diff_files)
print("same_tree          :", same_tree(SRC, RESTORED, ignore=()), "<- identical, __pycache__ was skipped on both sides by DEFAULT_IGNORES")

# Now corrupt one restored file and prove the comparison notices.
write(os.path.join(RESTORED, "docs", "readme.md"), "tampered!")
print("after tampering    : same_tree =", same_tree(SRC, RESTORED), "| diff in docs/:", filecmp.dircmp(SRC, RESTORED).subdirs["docs"].diff_files)
print("# Note: zip does not restore permissions/ownership by default - use tar if you need those back.")

# 22. Cleanup
# ------------------------------------
TMP.cleanup()
print("\n# 22. Cleanup - temp tree removed:", not os.path.exists(ROOT))

# 23. Summary - which tool for which file job
# ------------------------------------
# - Copy a file keeping timestamps        -> shutil.copy2
# - Copy / merge a folder                 -> shutil.copytree(dirs_exist_ok=True, ignore=...)
# - Delete a folder tree                  -> shutil.rmtree (no undo!)
# - Is a program installed?               -> shutil.which
# - Scratch file / folder                 -> tempfile (never invent /tmp names)
# - Find files by pattern                 -> glob (sorted!) | match name strings only -> fnmatch
# - List one folder with file info        -> os.scandir (not listdir + isfile)
# - Walk a tree and skip folders          -> os.walk + dirnames[:] = [...]
# - Save a file so a crash can't corrupt  -> write temp + fsync + os.replace
# - Are two files / folders the same?     -> filecmp.cmp(shallow=False) / dircmp
# - Only one instance may run             -> fcntl.flock (POSIX) / `filelock`
# - Bundle files                          -> zipfile (portable) / tarfile (keeps Unix metadata)
# - Extract an UNTRUSTED archive          -> validate names first; tar: filter="data"
# - Shrink one file or stream             -> gzip / bz2 / lzma (zlib for raw bytes)
# - Fake a file in memory                 -> io.StringIO / io.BytesIO
