# Logging — Notes

## What this covers
The `logging` module — the real tool for reporting what a program is doing, with severity levels, timestamps, and configurable output, instead of scattering `print()` everywhere.

## Key points
- **Levels, lowest to highest**: `DEBUG < INFO < WARNING < ERROR < CRITICAL`. `basicConfig(level=X)` shows `X` and everything more severe.
- **`logging.basicConfig(level=..., format=..., datefmt=...)`** — quick one-time setup for the root logger.
- **`logging.getLogger(__name__)`** — the recommended pattern: one logger per module. `__name__` is the module's dotted path, so it auto-slots into a hierarchy.
- **`logger.exception("msg")`** — call inside an `except` block to log the message plus the full traceback.
- **`FileHandler`** — write a logger's output to a file; `.setFormatter()` controls its format independently of other handlers.
- **`logger.propagate = False`** — stop a logger's messages from also bubbling up to its parent/root handlers (e.g. avoid double-printing).
- **Logger hierarchy** — loggers form a tree from dotted names (`"app"` is parent of `"app.module"`); a child's messages propagate up to every ancestor's handlers unless `propagate=False`.
- **`RotatingFileHandler`** (`logging.handlers`) — caps a log file at `maxBytes`, keeps `backupCount` rotated old copies once it's full.
- **`logging.config.dictConfig({...})`** — declarative setup for multiple loggers/handlers/formatters at once (e.g. loaded from JSON/YAML), instead of many imperative calls.
- **`extra={...}`** — attach custom fields (e.g. `user_id`) to a log record, usable in the format string as `%(user_id)s`.

## Gotchas (the part worth revising twice)
- Use `logging.getLogger(__name__)` per module, **not** one global/root logger — it lets you tune verbosity or redirect output per subsystem later, and log records carry their true origin.
- A child logger's messages propagate **up** the hierarchy by default — if you attach a handler to a child and also see duplicate output from the root, that's why; set `propagate = False` to stop it.
- `print()` is fine for quick one-off checks or CLI output meant for the end user; `logging` is for real applications where severity, timestamps, and per-module control matter.
- `RotatingFileHandler` rotates by file size (`maxBytes`), not by time — check `TimedRotatingFileHandler` if you need day/hour-based rotation instead.

## When it matters
Any application beyond a quick script — debugging production issues, tuning verbosity per subsystem without code changes, or writing structured logs to files/services.

## One-line recap example
```python
import logging
logger = logging.getLogger(__name__)          # one logger per module
logger.info("processing started")
```
