# Os And Sys — Notes

## What this covers
`os` (talk to the operating system: files, directories, env vars, processes) and `sys` (talk to the Python interpreter itself: args, path, exit codes), plus `subprocess` and `platform` for running commands and detecting the OS.

## Key points
- **`os.getcwd()`**, **`os.listdir(path)`** — current directory, its contents.
- **`os.makedirs(path, exist_ok=True)`** / **`os.rmdir(path)`** — create/remove directories.
- **`os.path`** — string-based path tools: `.join()`, `.basename()`, `.dirname()`, `.splitext()`, `.abspath()`, `.isfile()`/`.isdir()`.
- **`os.environ`** — dict-like access to environment variables; `os.environ["X"] = "y"` sets one for the current process.
- **`os.getenv(name, default)`** vs **`os.environ[name]`** — `getenv` returns a default safely, `environ[...]` raises `KeyError` if missing.
- **`os.walk(path)`** — recursively yields `(root, dirs, files)` for a directory tree.
- **`sys.argv`** — list of command-line arguments; `argv[0]` is the script name itself.
- **`sys.path`** — list of directories Python searches for imports.
- **`sys.version`**, **`sys.platform`** — interpreter version and OS platform string.
- **`sys.exit(code)`** — stops the script; `0` = success, non-zero = failure (checked by shells/CI).
- **`subprocess.run(["cmd", "arg"], capture_output=True, text=True)`** — run an external command; `.stdout`, `.returncode`.
- **`platform`** module — `.system()` ('Darwin'/'Linux'/'Windows'), `.release()`, `.machine()`, `.python_implementation()`.

## Gotchas (the part worth revising twice)
- **Always pass `subprocess.run()` a list of args, not a single string with `shell=True`** — a list avoids the argument being interpreted by a shell, which is how shell-injection bugs happen.
- `os.path` works with plain strings; `pathlib` (see file 05) is the modern object-oriented equivalent — prefer `pathlib` for new code.
- `os.getenv("X", default)` never raises; `os.environ["X"]` raises `KeyError` if unset — pick based on whether a missing var is actually an error.
- `sys.exit(code)` inside a subprocess only ends that subprocess — the convention `0=success` is what CI/shells check via `returncode`.

## When it matters
File/directory manipulation, reading config from environment variables, writing CLI scripts that need exit codes, or shelling out to another program safely.

## One-line recap example
```python
import subprocess
result = subprocess.run(["echo", "hi"], capture_output=True, text=True)
print(result.stdout.strip(), result.returncode)   # list of args, never shell=True
```
