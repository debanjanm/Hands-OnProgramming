# 01. Work Inside a Temp Sandbox
# 02. pathlib Essentials for Scripts
# 03. glob, rglob and fnmatch
# 04. Batch Rename
# 05. Organise Files by Extension
# 06. shutil: copy, move, tree copy, delete
# 07. Archives: zipfile, tarfile, make_archive
# 08. Hashing Files and Finding Duplicates
# 09. Watching a Directory by Polling
# 10. subprocess.run Safely
# 11. subprocess: Errors, Timeouts, Input
# 12. Scheduling: sched and threading.Timer
# 13. Environment Variables
# 14. Building an Email (Without Sending)
# 15. Retry Decorator
# 16. Idempotent Scripts
# 17. Dry-Run Pattern
# 18. Logging for Scripts
# 19. cron / launchd / Task Scheduler (notes)
# 20. Signal Handling (notes)

import fnmatch
import hashlib
import logging
import io
import os
import sched
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import zipfile
from email.message import EmailMessage
from functools import wraps
from pathlib import Path

# 01. Work Inside a Temp Sandbox
# ----------------------------
# - tempfile.TemporaryDirectory() creates a folder and deletes it (with contents) on exit.
# - Everything below lives in ONE sandbox so the demo leaves nothing behind.
# - Print paths relative to the sandbox: absolute temp paths differ on every run.

tmp = tempfile.TemporaryDirectory()
ROOT = Path(tmp.name)

def rel(path):
    return Path(path).relative_to(ROOT).as_posix()

def listing(folder=ROOT):
    return sorted(rel(p) for p in Path(folder).rglob("*") if p.is_file())

print("sandbox exists:", ROOT.is_dir())
print("sandbox empty:", listing() == [])

# 02. pathlib Essentials for Scripts
# ----------------------------
# - Path / "name" joins; .parent .name .stem .suffix .suffixes pick it apart.
# - mkdir(parents=True, exist_ok=True) is safe to repeat; write_text / read_text for small files.
# - exists(), is_file(), is_dir(); with_suffix / with_name build sibling names; stat().st_size.

work = ROOT / "work"
work.mkdir(parents=True, exist_ok=True)
work.mkdir(parents=True, exist_ok=True)  # second call: no error
f = work / "report.final.txt"
f.write_text("hello\n")
print(f.name, "|", f.stem, "|", f.suffix, "|", f.suffixes)
print(rel(f.with_suffix(".md")), rel(f.with_name("other.txt")))
print(f.stat().st_size, "bytes;", f.read_text().strip())
print(rel(f.parent), f.exists(), (work / "nope").exists())

# 03. glob, rglob and fnmatch
# ----------------------------
# - Path.glob("*.txt") matches in one folder; rglob("*.txt") searches all subfolders.
# - Results come in ARBITRARY order: wrap in sorted().
# - fnmatch.fnmatch(name, "*.py") tests a single name; it is case-sensitive on POSIX
#   only; use fnmatchcase to be explicit. fnmatch.filter filters a list.

for name in ("a.txt", "b.py", "c.TXT", "sub/d.txt", "sub/deep/e.py"):
    p = work / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(name)
print(sorted(rel(p) for p in work.glob("*.txt")))
print(sorted(rel(p) for p in work.rglob("*.py")))
print(fnmatch.fnmatchcase("c.TXT", "*.txt"), fnmatch.fnmatchcase("a.txt", "*.txt"))
print(fnmatch.filter(["x.py", "y.md", "z.py"], "*.py"))

# 04. Batch Rename
# ----------------------------
# - Build the full plan (old -> new) first, check for collisions, THEN rename.
# - Path.rename / shutil.move move files; Path.rename can overwrite on POSIX, so check exists().

batch = ROOT / "photos"
batch.mkdir()
for n in ("IMG 1.JPG", "IMG 2.JPG", "IMG 10.JPG"):
    (batch / n).write_text(n)
plan = {}
for src in sorted(batch.glob("*.JPG")):
    num = int(src.stem.split()[1])
    plan[src] = src.with_name(f"holiday_{num:03d}.jpg")
targets = list(plan.values())
assert len(set(targets)) == len(targets), "collision in plan"
for old, new in plan.items():
    if new.exists():
        continue
    old.rename(new)
print(listing(batch))
# Gotcha: on case-insensitive file systems (macOS, Windows) renaming IMG.JPG -> img.jpg
# is a no-op or an error in some tools: rename via a temporary name.

# 05. Organise Files by Extension
# ----------------------------
# - Classic script: sweep a messy folder into sub-folders by type.
# - Use a mapping suffix -> folder and a default ("other"); lower-case the suffix.

mess = ROOT / "downloads"
mess.mkdir()
for n in ("a.pdf", "b.PNG", "c.jpg", "d.txt", "noext", "e.py"):
    (mess / n).write_text(n)
KINDS = {".pdf": "docs", ".txt": "docs", ".png": "images", ".jpg": "images"}
for p in sorted(mess.iterdir()):
    if p.is_file():
        kind = KINDS.get(p.suffix.lower(), "other")
        (mess / kind).mkdir(exist_ok=True)
        shutil.move(str(p), str(mess / kind / p.name))
print(listing(mess))

# 06. shutil: copy, move, tree copy, delete
# ----------------------------
# - copy(src, dst) copies content+permissions; copy2 also copies timestamps.
# - copytree(src, dst) copies a folder (dirs_exist_ok=True to merge into an existing one).
# - move works across disks; rmtree deletes a whole folder: DOUBLE-CHECK the path first.
# - shutil.which("python3") finds executables on PATH; disk_usage(path) gives sizes.

src = ROOT / "tree_src"
(src / "inner").mkdir(parents=True)
(src / "one.txt").write_text("1")
(src / "inner" / "two.txt").write_text("2")
shutil.copytree(src, ROOT / "tree_copy")
print(listing(ROOT / "tree_copy"))
shutil.copy2(src / "one.txt", ROOT / "tree_copy" / "one_backup.txt")
shutil.copytree(src, ROOT / "tree_copy", dirs_exist_ok=True)
print(listing(ROOT / "tree_copy"))
shutil.rmtree(ROOT / "tree_copy")
print("after rmtree:", (ROOT / "tree_copy").exists())
print("which finds a python:", shutil.which("python3") is not None)

# 07. Archives: zipfile, tarfile, make_archive
# ----------------------------
# - zipfile.ZipFile(path, "w", ZIP_DEFLATED) then .write(file, arcname=...): arcname
#   controls the path INSIDE the archive (keep it relative).
# - tarfile.open(path, "w:gz") then .add(...). On extract, use filter="data" (3.12)
#   so malicious members (../../evil, absolute paths) are refused.
# - shutil.make_archive(base_name, "zip", root_dir) is the one-liner.
# - NEVER extractall an archive from an untrusted source without a safe filter ("zip slip").

arc = ROOT / "archives"
arc.mkdir()
with zipfile.ZipFile(arc / "t.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(src.rglob("*")):
        if p.is_file():
            z.write(p, arcname=p.relative_to(src).as_posix())
with zipfile.ZipFile(arc / "t.zip") as z:
    print("zip:", sorted(z.namelist()))
with tarfile.open(arc / "t.tar.gz", "w:gz") as t:
    t.add(src, arcname="proj")
with tarfile.open(arc / "t.tar.gz") as t:
    print("tar:", sorted(m.name for m in t.getmembers() if m.isfile()))
    out = ROOT / "untar"
    t.extractall(out, filter="data")
print("extracted:", listing(out))
made = shutil.make_archive(str(arc / "made"), "zip", root_dir=src)
print("make_archive ->", rel(made))
shutil.unpack_archive(made, ROOT / "unpacked")
print(listing(ROOT / "unpacked"))

# 08. Hashing Files and Finding Duplicates
# ----------------------------
# - Equal content -> equal hash. Compare sizes first (cheap), hash only candidates.
# - Read in chunks so huge files do not fill memory. sha256 is a good default.
# - md5/sha1 are fine for dedupe but NOT for security.

def file_hash(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()

dup = ROOT / "dups"
dup.mkdir()
(dup / "a.txt").write_text("same")
(dup / "b.txt").write_text("same")
(dup / "c.txt").write_text("different")
groups = {}
for p in sorted(dup.iterdir()):
    groups.setdefault(file_hash(p), []).append(p.name)
print(sorted(v for v in groups.values() if len(v) > 1))
print(hashlib.sha256(b"abc").hexdigest()[:16])

# 09. Watching a Directory by Polling
# ----------------------------
# - Simplest watcher: remember {name: (mtime, size)} and diff against a fresh scan.
# - Real tools use OS events (watchdog package, inotify, FSEvents) but polling is dependency-free.
# - ALWAYS bound the loop (max iterations or a deadline) so scripts can stop.

def snapshot(folder):
    return {p.name: p.stat().st_size for p in Path(folder).iterdir() if p.is_file()}

watched = ROOT / "inbox"
watched.mkdir()
before = snapshot(watched)
seen_events = []
for tick in range(4):
    if tick == 1:
        (watched / "new.txt").write_text("hi")
    if tick == 2:
        (watched / "new.txt").write_text("hi there")
    if tick == 3:
        (watched / "new.txt").unlink()
    after = snapshot(watched)
    for n in sorted(after.keys() - before.keys()):
        seen_events.append(f"tick {tick}: created {n}")
    for n in sorted(before.keys() - after.keys()):
        seen_events.append(f"tick {tick}: deleted {n}")
    for n in sorted(after.keys() & before.keys()):
        if after[n] != before[n]:
            seen_events.append(f"tick {tick}: modified {n}")
    before = after
    time.sleep(0.01)
print("\n".join(seen_events))
# Gotcha: coarse mtime resolution can hide fast edits - size or hash helps.

# 10. subprocess.run Safely
# ----------------------------
# - Pass the command as a LIST: subprocess.run([prog, arg1, arg2]). No shell involved,
#   so spaces and special characters in args are harmless.
# - shell=True with user input = command injection. Avoid it.
# - capture_output=True, text=True gives result.stdout / .stderr as str.
# - sys.executable is "the Python running me": no PATH surprises.

r = subprocess.run([sys.executable, "-c", "print('hi from child'); print(2 + 3)"],
                   capture_output=True, text=True, check=True)
print(r.returncode, r.stdout.splitlines())
user_input = "x; echo INJECTED"
r = subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1])", user_input],
                   capture_output=True, text=True)
print("as one harmless argument:", r.stdout.strip())

# 11. subprocess: Errors, Timeouts, Input
# ----------------------------
# - check=True raises CalledProcessError on nonzero exit (has .returncode, .stderr).
# - timeout=seconds raises TimeoutExpired and kills the child.
# - input="text" feeds stdin. env={...} sets the child environment. cwd= sets its folder.

try:
    subprocess.run([sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"],
                   check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print("failed with", e.returncode, "stderr:", e.stderr)
try:
    subprocess.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.3)
except subprocess.TimeoutExpired:
    print("timed out as expected")
r = subprocess.run([sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"],
                   input="piped in", capture_output=True, text=True)
print(r.stdout.strip())
r = subprocess.run([sys.executable, "-c", "import os; print(os.environ.get('MY_FLAG'), os.getcwd() == os.environ['W'])"],
                   env={**os.environ, "MY_FLAG": "on", "W": os.path.realpath(ROOT)}, cwd=ROOT,
                   capture_output=True, text=True)
print(r.stdout.strip())

# 12. Scheduling: sched and threading.Timer
# ----------------------------
# - sched.scheduler runs callables at relative delays, in order, inside run().
# - threading.Timer(delay, fn).start() runs fn once in another thread; .cancel() stops it.
# - Real jobs: cron/launchd, or APScheduler / Celery beat. Keep delays tiny in demos.

log_events = []
s = sched.scheduler(time.monotonic, time.sleep)
s.enter(0.06, 1, log_events.append, ("second",))
s.enter(0.02, 1, log_events.append, ("first",))
s.enter(0.10, 1, log_events.append, ("third",))
s.run()
print(log_events)
done = threading.Event()
t = threading.Timer(0.05, done.set)
t.start()
print("timer fired:", done.wait(timeout=1))
t2 = threading.Timer(5, print, ("never printed",))
t2.start()
t2.cancel()
t2.join()
print("cancelled timer alive:", t2.is_alive())

# 13. Environment Variables
# ----------------------------
# - os.environ is a dict-like of strings. .get(name, default) avoids KeyError.
# - Changes affect this process and its CHILDREN only, never the parent shell.
# - os.environ["X"] = 1 fails: values must be str.
# - Secrets: read from env, never hard-code them in scripts.

os.environ["DEMO_SCRIPT_VAR"] = "42"
print(os.environ.get("DEMO_SCRIPT_VAR"), os.environ.get("DEMO_MISSING", "fallback"))
try:
    os.environ["DEMO_BAD"] = 1
except TypeError as e:
    print("TypeError:", e)
print(int(os.environ.get("DEMO_SCRIPT_VAR", "0")) + 1)
del os.environ["DEMO_SCRIPT_VAR"]
print("DEMO_SCRIPT_VAR" in os.environ)
print("expandvars:", os.path.expandvars("$NOT_SET_ANYWHERE_XYZ/x"))

# 14. Building an Email (Without Sending)
# ----------------------------
# - EmailMessage builds a proper MIME message: headers, text body, HTML alternative,
#   attachments. Building is local and safe.
# - Sending would be smtplib.SMTP(host).send_message(msg) with credentials from env:
#   we deliberately do NOT do that here.
# - Never build headers by string concatenation with user input (header injection):
#   EmailMessage rejects newlines in header values.

msg = EmailMessage()
msg["From"] = "bot@example.com"
msg["To"] = "team@example.com"
msg["Subject"] = "Nightly report"
msg.set_content("Plain text body.\nAll jobs finished.")
msg.add_alternative("<p>All jobs <b>finished</b>.</p>", subtype="html")
msg.add_attachment(b"a,b\n1,2\n", maintype="text", subtype="csv", filename="report.csv")
print(msg["Subject"], "|", msg.get_content_type())
print([part.get_content_type() for part in msg.walk()])
print([p.get_filename() for p in msg.iter_attachments()])
try:
    msg["X-Test"] = "ok\nBcc: evil@example.com"
except ValueError as e:
    print("header injection refused:", type(e).__name__)

# 15. Retry Decorator
# ----------------------------
# - Flaky things (network, locks) deserve a bounded retry with a growing delay.
# - Retry only exceptions that are plausibly temporary; re-raise the last one.
# - Keep the number of attempts small and always have a cap.

def retry(times=3, delay=0.01, exceptions=(OSError,)):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            for attempt in range(1, times + 1):
                try:
                    return fn(*a, **kw)
                except exceptions as e:
                    if attempt == times:
                        raise
                    print(f"  attempt {attempt} failed ({e}); retrying")
                    time.sleep(delay * 2 ** (attempt - 1))
        return wrapper
    return deco

calls = {"n": 0}

@retry(times=3)
def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise OSError("temporary glitch")
    return "ok after %d calls" % calls["n"]

print(flaky())

@retry(times=2)
def always_bad():
    raise OSError("down")

try:
    always_bad()
except OSError as e:
    print("gave up:", e)
print(flaky.__name__, "<- functools.wraps keeps the name")

# 16. Idempotent Scripts
# ----------------------------
# - Idempotent = running twice gives the same result as running once. Crucial because
#   schedulers retry and humans re-run.
# - Tools: mkdir(exist_ok=True), "if not exists", write to a temp file then os.replace
#   (atomic), skip work whose output already exists, use sets not appends.

target = ROOT / "state" / "config.txt"

def ensure_config(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() == content:
        return "unchanged"
    tmpfile = path.with_suffix(".tmp")
    tmpfile.write_text(content)
    os.replace(tmpfile, path)  # atomic on the same filesystem
    return "written"

print(ensure_config(target, "v=1"), ensure_config(target, "v=1"), ensure_config(target, "v=2"))
print(listing(ROOT / "state"))

# 17. Dry-Run Pattern
# ----------------------------
# - A --dry-run flag prints what WOULD happen and changes nothing.
# - Put every side effect behind ONE function that checks the flag, so no action can
#   forget it. Default to dry-run for dangerous scripts.

def act(dry_run, description, fn, *args):
    if dry_run:
        print("[dry-run] would", description)
        return
    print("[do]", description)
    fn(*args)

junk = ROOT / "junk.tmp"
junk.write_text("x")
act(True, "delete junk.tmp", junk.unlink)
print("still there after dry run:", junk.exists())
act(False, "delete junk.tmp", junk.unlink)
print("gone after real run:", not junk.exists())

# 18. Logging for Scripts
# ----------------------------
# - Prefer logging over print for scripts: levels, timestamps, one switch for verbosity.
# - Humans see INFO on the console; keep DEBUG for a file or -v. Never log secrets.
# - Here a StringIO handler (no timestamp) keeps output deterministic.

buf = io.StringIO()
h = logging.StreamHandler(buf)
h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
lg = logging.getLogger("script.demo")
lg.setLevel(logging.INFO)
lg.propagate = False
lg.addHandler(h)
lg.debug("not shown (below INFO)")
lg.info("processed %d files", 3)
lg.warning("skipped %s", "locked.txt")
try:
    1 / 0
except ZeroDivisionError:
    lg.exception("step failed")  # includes traceback
text = buf.getvalue().splitlines()
print(text[0])
print(text[1])
print(text[2], "+ traceback lines:", len(text) > 3)
lg.removeHandler(h)

# 19. cron / launchd / Task Scheduler (notes)
# ----------------------------
# - cron (Linux/macOS): `crontab -e`, line format:  min hour day month weekday  command
#       30 2 * * *  /usr/bin/python3 /home/me/backup.py >> /home/me/backup.log 2>&1
#   cron has a tiny PATH and no shell profile: use absolute paths and pass env explicitly.
# - launchd (macOS): a .plist in ~/Library/LaunchAgents with Label, ProgramArguments,
#   StartCalendarInterval or StartInterval; load with `launchctl load`.
# - Windows Task Scheduler: `schtasks /create /sc daily /tn Backup /tr "python C:\\backup.py" /st 02:30`
# - Make the script idempotent, log to a file, return nonzero on failure, avoid overlap
#   (lock file) when a run may outlast the interval.

print("schedulers call your script; the script itself stays a normal CLI")

# 20. Signal Handling (notes)
# ----------------------------
# - Ctrl+C raises KeyboardInterrupt (SIGINT). Catch it in main for a clean exit
#   (usually code 130), and use try/finally for cleanup.
# - signal.signal(signal.SIGTERM, handler) lets a service shut down gracefully when
#   stopped by systemd/Docker/kill. Handlers run in the main thread only.
# - Keep handlers tiny: set a flag (threading.Event) and let the main loop exit.
# - SIGKILL cannot be caught. Windows supports only a few signals.
# - Registering handlers changes global process state; here we only read the default.

import signal

print("default SIGINT handler is Python's:", signal.getsignal(signal.SIGINT) is signal.default_int_handler)
stop = threading.Event()
signal.signal(signal.SIGTERM, lambda signum, frame: stop.set())
os.kill(os.getpid(), signal.SIGTERM)
print("SIGTERM handled by flag:", stop.wait(timeout=1))
signal.signal(signal.SIGTERM, signal.SIG_DFL)

tmp.cleanup()
print("sandbox removed:", not ROOT.exists())
