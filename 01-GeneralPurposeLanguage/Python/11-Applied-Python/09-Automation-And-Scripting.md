# Automation and Scripting — Notes

## What this covers
Everyday automation: pathlib/shutil file work, batch rename and organise, archives, hashing for dedupe, polling a folder, running subprocesses safely, scheduling, environment variables, building (not sending) email, retries, idempotency, dry runs, and logging for scripts.

## Key points
- Practise inside `tempfile.TemporaryDirectory()`; it cleans up after itself.
- `Path` joins with `/`; `glob` / `rglob` find files; `fnmatch` tests names. Always `sorted()` results.
- Build the whole rename/move plan first, check for collisions, then act.
- `shutil`: `copy2`, `copytree(dirs_exist_ok=True)`, `move`, `rmtree`, `make_archive`, `unpack_archive`, `which`.
- zipfile/tarfile: control paths inside the archive with `arcname`; extract tar with `filter="data"`.
- Dedupe: group by size, then by chunked `sha256`.
- Polling watcher: diff two `{name: size}` snapshots, with a bounded loop.
- `subprocess.run([list, of, args], capture_output=True, text=True, check=True, timeout=...)`; use `sys.executable` for Python children.
- `sched` and `threading.Timer` for in-process scheduling; cron/launchd/Task Scheduler for real schedules.
- `EmailMessage` builds MIME messages locally; sending is a separate, deliberate step.
- Retry with a bounded count and growing delay; write idempotent scripts (atomic `os.replace`, "if not exists"); add `--dry-run` through one gate function.

## Gotchas (the part worth revising twice)
- `glob` order is arbitrary — sort before printing or acting.
- `shell=True` with user input is command injection; a list of args treats `x; rm -rf` as plain text.
- `extractall` on untrusted archives can write outside the target ("zip slip").
- `shutil.rmtree` on the wrong variable is unrecoverable — print and check first.
- Case-insensitive file systems make case-only renames tricky.
- `os.environ` values must be `str`; changes never reach the parent shell.
- mtime can have coarse resolution; compare size or hash too.
- Retrying non-temporary errors (bad input) just wastes time — retry only plausible transient exceptions.
- cron runs with a tiny PATH and no profile; use absolute paths.
- Signal handlers must be tiny (set a flag); SIGKILL cannot be caught.

## When it matters
Backups, file cleanup, report generation, glue between tools. Scripts that are safe to re-run, preview with `--dry-run`, and log clearly are the ones that survive being scheduled.

## One-line recap example
```python
import subprocess, sys
out = subprocess.run([sys.executable, "-c", "print(2 + 3)"], capture_output=True, text=True, check=True)
print(out.stdout.strip())
```
