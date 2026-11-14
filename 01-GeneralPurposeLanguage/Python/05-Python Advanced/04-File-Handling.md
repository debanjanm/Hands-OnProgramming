# File Handling — Notes

## What this covers
Reading and writing files with `open()`, the `with` statement, file modes, binary vs text data, and memory-efficient handling of large files.

## Key points
- `open(path, mode)` returns a file object. Always use `with open(...) as f:` — it auto-closes the file even if an error occurs inside the block.
- Modes: `'r'` read (default), `'w'` write (overwrites!), `'a'` append, `'x'` exclusive create (errors if file exists), `'b'` binary, `'t'` text (default), `'+'` read+write.
- Reading: `f.read()` (whole file), `for line in f:` (memory-efficient, line by line), `f.readline()` (one line), `f.readlines()` (list of all lines).
- Writing: `f.write(str)` for one chunk, `f.writelines(list_of_strs)` for many at once (does NOT add newlines for you).
- `f.seek(offset)` moves the cursor; `f.tell()` reports its current position.
- Binary mode (`'rb'`/`'wb'`) works with `bytes` objects instead of `str` — use `.decode()`/`.encode()` to convert.
- `os.path.exists(path)` checks before opening; opening a missing file in `'r'` mode raises `FileNotFoundError`.
- `tempfile.NamedTemporaryFile()` creates a scratch file that's auto-deleted when the `with` block exits.
- `shutil.copy()` copies a file's content + permissions; `shutil.move()` relocates/renames.

## Gotchas (the part worth revising twice)
- **Always pass `encoding="utf-8"` explicitly.** Without it, Python uses the OS's default text encoding, which differs across machines — a file written on one machine can fail to read correctly on another.
- Buffering: default is a full OS-sized buffer, flushed when full or on close. `buffering=1` is line-buffered (text mode only, flushes on `\n`). `f.flush()` forces buffered data out immediately without closing — useful for logs you want visible right away.
- For **text** files, iterate line by line (`for line in f`) — memory-efficient because it never loads the whole file. For files without natural line breaks (binary, huge single-line data), read fixed-size chunks with `f.read(chunk_size)` in a loop instead — plain `f.read()` loads everything into memory at once.
- `'w'` mode silently overwrites/truncates existing content — easy to lose data by using the wrong mode.

## When it matters
Any time your program needs to persist data, read config/data files, process logs, or handle datasets too large to comfortably fit in memory.

## One-line recap example
```python
with open("data.txt", "r", encoding="utf-8") as f:
    for line in f:          # one line in memory at a time
        print(line.strip())
```
