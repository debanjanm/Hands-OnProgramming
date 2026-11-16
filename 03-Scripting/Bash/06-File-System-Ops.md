# Bash File System Ops — Notes

## What this covers
Safe temp-file handling with `mktemp` + `trap`, file test operators, `find`, `chmod`, and piping `find` results into `xargs`.

## Key points
- `mktemp -d` creates a uniquely-named temp directory (no collisions between concurrent runs) and prints its path.
- `trap 'cmd' EXIT` registers cleanup that runs on any script exit (normal, `exit`, or error) — write cleanup once instead of repeating it at every exit point.
- File tests: `-e` exists, `-f` exists and is a regular file, `-d` exists and is a directory, `-r`/`-w`/`-x` readable/writable/executable.
- `find dir -type f -name "*.txt"` finds files by type and name pattern; `-type d` finds directories.
- `chmod`: numeric (`755` = owner rwx, group r-x, other r-x, always sets exactly) vs symbolic (`u=rw,g=r,o=`, can be relative like `+x` or exact like `=`).
- `xargs` reads lines from stdin and builds/runs a command with them as arguments (auto-batches for very long lists). `-I{}` substitutes each line into `{}` when the argument needs to appear somewhere other than the end.

## Gotchas (the part worth revising twice)
- Set the `trap ... EXIT` up immediately after creating the temp dir/file — if something fails between creation and the trap, cleanup never registers and you leak temp files.
- `find | xargs` breaks on filenames with spaces or newlines unless you use `find -print0 | xargs -0` — the plain pipe here works because the demo filenames are simple, but it's not safe in general.
- Numeric `chmod` always sets permissions exactly (wipes anything not specified); symbolic `chmod +x` only adds to what's already there. Don't mix them up when you actually care about existing permissions.

## When it matters
Any script that creates scratch files/directories — the `mktemp -d` + `trap EXIT` pattern is the standard way to guarantee cleanup even if the script errors out partway through.

## One-line recap example
```bash
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT   # cleanup guaranteed, no matter how the script exits
```
