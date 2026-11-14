# Error and Exception Handling — Notes

## What this covers
How Python handles errors at runtime: `try`/`except`/`else`/`finally`, raising your own exceptions, building custom exception hierarchies, and newer tools like exception groups and `contextlib.suppress`.

## Key points
- Syntax errors are caught before the program runs; exceptions happen during execution and can be caught and handled.
- `try/except` can catch a single type, multiple types in one `except (A, B):`, or multiple separate `except` clauses.
- `else:` runs only if the `try` block raised nothing; `finally:` always runs (cleanup), exception or not.
- `raise SomeError("message")` raises manually; custom exceptions are just classes inheriting from `Exception` (or a more specific built-in), often storing extra data in `__init__` before calling `super().__init__(...)`.
- `raise NewError(...) from original_error` chains exceptions — the original is preserved on `.__cause__` for debugging.
- Exception hierarchy: `BaseException -> Exception -> ValueError/TypeError/KeyError/IndexError/...`. Catching a base class also catches its subclasses.
- Design your own hierarchy the same way: one base exception per app/module, specific subclasses per failure mode — callers can catch the base for "any of these" or a subclass for one specific case.
- `contextlib.suppress(SomeError)` is a cleaner alternative to a `try/except: pass` block when you genuinely want to ignore a specific exception.
- `traceback.format_exc()` gets the full traceback as a string, for logging instead of just letting it print to stderr.
- Exception Groups + `except*` (Python 3.11+): `ExceptionGroup` bundles several unrelated exceptions raised together (common in concurrent code); `except*` matches by type inside the group and can run more than one `except*` clause for a mixed-type group.
- **Chaining**: an exception raised while handling another is auto-linked on `__context__` (traceback says "During handling of the above exception, another exception occurred"). `raise X from Y` sets `__cause__` instead ("The above exception was the direct cause of..."). `raise X from None` hides the context (`__suppress_context__ = True`) — use it only when the original is an internal detail.
- **Nested handlers**: inner code translates low-level errors into your layer's error (`raise ConfigError(...) from e`); outer code only catches your layer's type.
- **Keep `try` narrow**: put only the risky line in `try`, the rest in `else:`, so errors from unrelated code are not mis-caught.
- `Exception` vs `BaseException`: `KeyboardInterrupt`, `SystemExit`, `GeneratorExit` are *not* `Exception` subclasses — `except Exception` lets them through; bare `except:` does not.
- `e.add_note("...")` (3.11+) attaches context shown in the traceback (`e.__notes__`). `sys.exc_info()` = `(type, value, tb)` of the exception being handled, `(None, None, None)` otherwise.
- **Warnings** (`warnings.warn`) report without stopping; filters can `ignore` them or turn them into exceptions (`simplefilter("error")`, `python -W error`).
- **EAFP** (try it, handle failure) is the Pythonic style and avoids check-then-use races; **LBYL** (check first) fits when failure is common or the action is not safely undoable.

## Gotchas (the part worth revising twice)
- Bare `raise` (inside an `except`) re-raises the current exception with its **original traceback intact**. `raise e` raises the same object but adds a new frame, making it look like the error started at that re-raise line. Prefer bare `raise` when re-raising.
- `except*` is new **syntax**, not just a new runtime feature — it won't even parse on Python < 3.11, so guard any code using it (e.g. behind a `sys.version_info` check, or keep it out of files that must import on older Python).
- Catching `Exception` broadly (or a shared base class) is convenient but can hide bugs you didn't mean to catch — catch the narrowest type that makes sense.
- `with` statements/context managers guarantee cleanup even when an exception occurs — functionally like `try/finally`, covered in depth in the Context-Managers file.
- An exception raised inside `finally` or `except` **replaces** the original (it survives only on `__context__`), so `except OriginalType` upstream misses it. Wrap risky cleanup in its own `try/except`.
- `return`/`break`/`continue` inside `finally` silently **swallows** the in-flight exception. Use `finally` for cleanup only.
- Bare `except:` also swallows Ctrl+C and `sys.exit()` — use `except Exception:` at the broadest.
- In a loop, put `try/except` *inside* it (`continue` to skip a bad item, `break` on a fatal one); outside the loop, the first failure ends everything.

## When it matters
Any code that talks to the outside world (files, network, user input, parsing) needs this — to fail predictably instead of crashing, and to give callers a clear, catchable signal about what went wrong.

## One-line recap example
```python
try:
    raise ValueError("bad value")
except ValueError as e:
    raise RuntimeError("wrapped failure") from e   # chains original as __cause__
```
