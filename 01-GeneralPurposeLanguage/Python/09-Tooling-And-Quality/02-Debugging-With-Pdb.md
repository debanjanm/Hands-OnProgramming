# Debugging With Pdb — Notes

## What this covers
A step-by-step way to find bugs: read the traceback, reproduce, isolate, guess, test the guess. Then the tools: good print debugging, `logging`, `assert`, `breakpoint()`, the `pdb` commands, post-mortem debugging, `faulthandler`, tracing, interpreter flags, a catalogue of classic bugs, and bisecting.

## Key points
- **Read a traceback from the bottom**: the last line says WHAT failed, the frame above it says WHERE, frames higher up say HOW we got there. The bug is often further up, where the bad data was created. "Direct cause of" means chained errors: find the original one.
- **Loop**: reproduce, isolate (shrink the input), hypothesize (a sentence you can disprove), verify (change one thing), fix, add a regression test.
- **Print debugging done well**: `print(f"{x=}")`, `repr()` / `!r` (shows trailing spaces, `'3'` vs `3`), `pprint` for nested data, print to `stderr`.
- **`logging` over `print`** when output should stay: levels, function names, switch on/off without editing code. `logger.exception(...)` logs the traceback.
- **`assert` documents what must be true.** `python -O` removes all asserts.
- **`breakpoint()`** opens pdb. `PYTHONBREAKPOINT=0` turns every one off; `=pdb.set_trace` is the default; `=pkg.func` calls your own hook.
- **pdb commands**: `l` / `ll` list code, `n` next (step over), `s` step into, `r` run until return, `c` continue, `p` / `pp` print, `a` args, `w` stack, `u` / `d` up / down the stack, `q` quit, `!stmt` run any Python (e.g. `!total = 5`), `display expr`, `until [line]`, `j line` jump.
- **Breakpoints**: `b func`, `b file:line`, `b line, cond` (conditional), `condition N expr`, `tbreak` (once), `cl N`, `b` (list), `commands N` (run commands on hit; `silent` + `print(...)` + `c` = logpoint).
- **Post-mortem** (inspect after a crash): `python -m pdb -c continue script.py`, `pdb.post_mortem(tb)`, `pdb.pm()` (uses `sys.last_traceback`), `pytest --pdb`.
- **`traceback` module**: `format_exc()` gives the text, `extract_tb()` gives frames, `extract_stack()` shows how you got here, `exc.add_note()` adds context.
- **`faulthandler`**: `enable()` prints stacks when Python crashes; `dump_traceback_later(t)` is a hang watchdog (cancel it when done); `-X faulthandler` or `PYTHONFAULTHANDLER=1` turns it on without code changes.
- **`sys.settrace`** sees every call/line/return (how debuggers work); `sys.setprofile` sees only calls/returns. Always reset with `settrace(None)`.
- **`inspect.stack()`** tells you who called a function (slow; `sys._getframe(1)` is cheaper).
- **Flags**: `-W error` turns warnings into exceptions, `-X dev` finds unclosed files and more, `-X importtime` times imports.
- **Bisect**: with a clean good/bad split, halving finds the first bad version in about log2(N) tests (`git bisect run <test>`). Works on data and code too.

## Gotchas (the part worth revising twice)
- Never use `assert` to validate user input: it vanishes with `-O`. `assert (cond, "msg")` is always true.
- A variable named like a command (`n`, `c`, `s`, `l`) is run as the command in pdb. Use `p n` or `!n`.
- `!x = 1` then `j` right after can lose the assignment; assign after jumping.
- A forgotten `breakpoint()` hangs CI. Set `PYTHONBREAKPOINT=0` there.
- Classic bugs and tells: mutable default argument (`f.__defaults__`), late-binding closure (`[lambda: i ...]` gives all the same value), off-by-one (test 0, 1, first, last), shadowed builtin (`'list' object is not callable`), removing from a list while looping, `is` instead of `==`, `//` floors (`-7 // 2 == -4`), `except Exception: return 0` hiding real errors, relative paths depending on the current folder (use `Path(__file__).parent`), circular imports (`partially initialized module`).
- After `u` in pdb you inspect the caller's variables; the program is still stopped in the lower frame.
- `inspect.stack()` and kept frame objects are slow and can leak memory.

## When it matters
Whenever the cause is not obvious in two minutes. Start with the cheapest tool (`f"{x=}"`, `assert`), move to `breakpoint()`, use post-mortem for crashes, `faulthandler` for hangs and segfaults.

## One-line recap example
```python
def total(prices):
    breakpoint()                  # stops here; try: p prices, n, s, w, c
    return sum(prices)

# run with PYTHONBREAKPOINT=0 python app.py   -> breakpoint() does nothing
# crash? run: python -m pdb -c continue app.py   -> inspect with w, u, p var
```
