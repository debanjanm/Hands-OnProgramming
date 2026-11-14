# Context Managers — Notes

## What this covers
The `with` statement: how it guarantees setup/cleanup around a block of code (even on error), how to write your own context managers as classes or generators, and handling a variable number of them at once.

## Key points
- A context manager sets up a resource, hands control to a block, then guarantees cleanup afterward — used via `with`. `open()` is the classic built-in example.
- `with` replaces a manual `try/finally` — same guarantee, less error-prone, less boilerplate.
- Class-based context manager: implement `__enter__` (setup, returns the resource) and `__exit__(exc_type, exc_value, traceback)` (cleanup). `__exit__` returning `True` suppresses the exception; `False` (or `None`) lets it propagate.
- Function-based context manager: `@contextlib.contextmanager` on a generator function — code before `yield` is the `__enter__` half, code after (typically in a `finally`) is the `__exit__` half.
- One `with` statement can open multiple managers: `with open(a) as f1, open(b) as f2:`.
- `contextlib.ExitStack` handles a number of context managers decided at **runtime** (e.g. one file per item in a list) — enter each via `stack.enter_context()`, and they all exit in reverse order when the `with` block ends, even on error.
- `contextlib.suppress(SomeError)` is itself a context manager that turns a specific exception into a no-op.
- Async context managers use `__aenter__`/`__aexit__` (both coroutines) with `async with` — full depth in the Async-Await file.

## Gotchas (the part worth revising twice)
- **Reusable vs reentrant**: most `@contextmanager`-based generators are only *reusable* (same instance, separate `with` blocks one after another) but NOT *reentrant* (same instance nested inside itself). Nesting the same `@contextmanager` instance reuses the already-exhausted generator and raises an error.
- `__exit__`'s return value matters: returning `True` silently swallows the exception — easy to accidentally suppress errors you meant to let propagate if you're not careful with the return logic.
- Class-based context managers give you more control (state across `__enter__`/`__exit__`, reentrancy if you design for it); generator-based ones are shorter to write but inherit the reusable-not-reentrant limitation above.

## When it matters
Anywhere you need guaranteed cleanup — files, locks, DB connections, network sockets — especially when the cleanup must happen even if the code in between raises an exception.

## One-line recap example
```python
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    print(f"acquire {name}")
    try:
        yield name
    finally:
        print(f"release {name}")   # always runs, even on exception
```
