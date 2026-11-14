# Enum — Notes

## What this covers
The `enum` module — defining a fixed set of named constants, safer and clearer than scattering raw strings or magic numbers through code.

## Key points
- **`class Color(Enum): RED = 1 ...`** — access members as `Color.RED`, with `.name` and `.value`.
- **`auto()`** — auto-assigns values so you don't have to pick numbers yourself.
- **Enum members are singletons** — `current is Status.ACTIVE` works, not just `==`.
- **Iterate** an enum class directly (`for s in Status`) to get all members.
- **Lookup** — `Status(1)` by value, `Status["ACTIVE"]` by name.
- **`IntEnum`** — members also behave like real ints (comparable, addable) — useful when you need enum safety but int compatibility (e.g. priorities).
- **`Flag` / `IntFlag`** — combinable bitwise enums; OR members together (`READ | WRITE`), test with `in`. `IntFlag` also behaves like an int (chmod-style values).
- **Custom methods/properties** — an Enum class can define `@property` and regular methods, using `self.value` for computation.
- **`@unique`** — decorator that forbids two members from sharing the same value (plain `Enum` silently allows duplicates as aliases).
- **`StrEnum`** (3.11+) or the pre-3.11 `class Role(str, Enum)` pattern — members that ARE strings (`isinstance(Role.ADMIN, str)` is `True`, compares equal to raw strings).
- **`_missing_`** — a classmethod hook called when a value doesn't match any member directly; lets you normalize input (e.g. case-insensitive lookup) before falling back to `ValueError`.

## Gotchas (the part worth revising twice)
- Without `@unique`, an `Enum` with two members sharing the same value silently makes the second one an *alias* of the first — no error, easy to miss.
- `IntEnum`/`IntFlag` give up some of Enum's type safety (they behave like plain ints), trading it for numeric compatibility — pick deliberately.
- `Flag` members combine with `|` and check with `in` — don't reach for a list/set of enums when a `Flag` says what you mean more directly.
- `_missing_` returning `None` means "no match" — the normal `ValueError` still gets raised; it's only a hook to normalize *before* failing, not to suppress failure entirely.

## When it matters
Anywhere you'd otherwise use magic strings/numbers for a fixed set of options — statuses, roles, permissions, directions — where typos should be caught early instead of failing silently.

## One-line recap example
```python
from enum import Enum
class Status(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
print(Status.ACTIVE == Status.ACTIVE)   # True, and it's a real singleton, not a raw string
```
