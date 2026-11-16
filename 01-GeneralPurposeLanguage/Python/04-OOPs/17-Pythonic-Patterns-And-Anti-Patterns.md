# Pythonic Patterns And Anti-Patterns — Notes

## What this covers
Patterns that fit Python naturally (registry via decorators and `__init_subclass__`, dependency injection, context managers, EAFP, Repository and Unit of Work, Result/Option returns, dataclass value objects) and common anti-patterns (god object, mutable default arguments, inheritance for reuse, Java-style getters/setters, singleton abuse, premature abstraction, stringly-typed code), plus a code smell cheat sheet and a before/after refactor.

## Key points
- **Registry**: a decorator adds each function to a dict, so a new handler needs no edits elsewhere. `__init_subclass__` does the same automatically for subclasses.
- **Dependency injection**: pass collaborators in (constructor or argument) instead of creating them inside. No framework needed; a `Protocol` describes the shape you expect.
- **Context manager**: `with` guarantees cleanup. Use `@contextmanager` with `try/finally`, or `__enter__`/`__exit__`.
- **EAFP** ("try it, handle the error") is preferred over **LBYP** ("check first"): shorter, and avoids check-then-use races. Catch specific exceptions.
- **Repository**: a collection-like interface (`add`, `get`, `all`) hiding where data lives. **Unit of Work**: group changes and commit or roll back together; a context manager fits.
- **Result/Option**: return `Ok(value)` or `Err(reason)` (or `Optional`) where failure is expected, and handle it with `match`.
- **Value objects**: `@dataclass(frozen=True)` gives named fields, equality by value, hashing, and immutability; use `replace()` to "change" one.
- **Anti-patterns**: god object, mutable defaults, inheritance for reuse, getters/setters, singleton abuse, premature abstraction, stringly-typed code. Each has a short fix (split, `None` default, composition, plain attribute/`@property`, pass an object in, wait for 3 cases, `Enum`).

## Gotchas (the part worth revising twice)
- **Mutable default arguments** are created once at definition time and shared by every call: `def f(x, bucket=[])` keeps growing. Use `None` and build inside (dataclasses use `field(default_factory=list)`).
- `__init_subclass__` and decorator registries run at **import time**; if a module is never imported, its plugins are never registered.
- `__exit__` returning a truthy value **swallows** the exception. Return `False`/`None` unless you mean to suppress.
- Never use a bare `except:`; it hides real bugs and catches `KeyboardInterrupt`. EAFP means catching the *specific* expected error.
- Subclassing `list` to build a stack **leaks** `insert`, `sort`, etc. Composition gives a small honest API.
- A `Singleton` class is global state in disguise. A module-level object is already a singleton in Python; better still, inject it.
- **Rule of three**: duplication is cheaper than the wrong abstraction. Abstract on the third real case, or at a boundary you must fake in tests.
- Frozen dataclasses stop attribute assignment, but a **mutable field inside** (a list) can still change.
- Don't wrap an ORM in a Repository just because the pattern exists; that is a second layer for no gain.

## When it matters
These decide whether code stays easy to test and extend. Use injection and repositories at boundaries (email, database), context managers wherever setup and cleanup pair up, `Enum` and frozen dataclasses for clear data, and run the smell checklist in code review. Treat the anti-patterns as hints to look closer, not as laws.

## One-line recap example
```python
def add_item(item, bucket=None):      # not bucket=[]
    bucket = [] if bucket is None else bucket
    bucket.append(item)
    return bucket
```
