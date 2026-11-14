# Pathlib Module — Notes

## What this covers
`pathlib.Path` — the modern, object-oriented way to work with filesystem paths, replacing string-based `os.path`.

## Key points
- **`Path("a") / "b"`** — join paths with `/` instead of `os.path.join()`.
- **Components** — `.name`, `.stem` (name without suffix), `.suffix`, `.parent`, `.parts`.
- **Checks** — `.exists()`, `.is_dir()`, `.is_file()`, `.is_absolute()`.
- **Filesystem ops** — `.mkdir(exist_ok=True)`, `.rmdir()`, `.write_text()` / `.read_text()`, `.unlink()` (delete file).
- **`.iterdir()`** — list a directory's direct contents. **`.glob(pattern)`** — pattern-match files; needs explicit `**` to recurse (`glob("**/*.py")`). **`.rglob(pattern)`** — shorthand that's always recursive.
- **`.resolve()`** — get the absolute, fully resolved path.
- **`.with_suffix(".json")`** / **`.with_name("new.txt")`** — return a new `Path` with just that piece changed.
- **`.stat()`** — file metadata: `.st_size`, `.st_mtime` (modification time, as a timestamp).
- **`PurePosixPath` / `PureWindowsPath`** — pure string manipulation for paths from a *different* OS, no filesystem access. `Path` itself is OS-specific and *does* touch the real filesystem.
- **`Path.home()`** / **`Path("~/data").expanduser()`** — resolve the user's home directory / `~`.

## Gotchas (the part worth revising twice)
- `glob("*.py")` only searches the current directory — you need `glob("**/*.py")` (with `**`) to recurse. `rglob("*.py")` is the recursive shortcut, equivalent to `glob("**/*.py")`.
- `PurePath` types never touch disk (safe to build paths for an OS you're not running), while `Path` is concrete and OS-specific — don't call `.exists()` on a `PureWindowsPath` from Linux, it's not meant to.
- `.with_suffix()`/`.with_name()` return a *new* `Path` — they don't mutate the original.
- Prefer `pathlib` over `os.path` in new code — same capability, more readable (`Path('a') / 'b'` vs `os.path.join('a', 'b')`).

## When it matters
Any code touching the filesystem — reading/writing files, walking directories, building cross-platform paths, or inspecting file metadata.

## One-line recap example
```python
from pathlib import Path
p = Path("data") / "report.txt"
p.parent.mkdir(exist_ok=True)
p.write_text("hello")          # object-oriented, no os.path.join needed
```
