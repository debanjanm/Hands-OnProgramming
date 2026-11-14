# Typing And Type Hints — Notes

## What this covers
The `typing` module's generic/composite type hints — annotations that document expected types for tools like mypy, but are never enforced by Python itself at runtime.

## Key points
- **Type hints are not enforced at runtime** — `def add(a: int, b: int)` still happily accepts strings and concatenates them; only a static checker (mypy) flags it.
- **Generics** — `List[int]`, `Dict[str, int]`, `Tuple[int, int]` describe container contents.
- **`Optional[X]`** — same as `Union[X, None]`, a value or `None`.
- **`Union[X, Y]`** — one of several types.
- **`Callable[[int, int], int]`** — a function signature as a type (args list, then return type).
- **`TypeVar`** — makes a function generic (`List[T] -> T`), so the checker ties the input/output types together.
- **`Protocol`** — structural typing ("duck typing but checkable"): any object with the right methods satisfies it, no inheritance required.
- **`TypedDict`** — a dict with a known, fixed shape of keys/types.
- **Modern syntax (3.9+/3.10+)** — `list[int]` instead of `List[int]`, `dict[str,int]` instead of `Dict`, `int | None` instead of `Optional[int]`, `int | str` instead of `Union[int, str]` — no import needed.
- **`Literal["a","b"]`** — restrict a value to a specific fixed set of literals.
- **`Final`** — marks a name that shouldn't be reassigned (checker-enforced only).
- **`@overload`** — declare multiple valid signatures for one function; the real implementation goes last, undecorated.
- **`NewType`** — a distinct type for the checker (e.g. `UserId`) that's still the same type at runtime (zero overhead).
- **`TYPE_CHECKING`** — guard imports that are only needed for type hints; code under `if TYPE_CHECKING:` never runs.
- **`Any` vs `object`** — `Any` turns off checking entirely; `object` is a real type requiring narrowing before type-specific methods can be called.
- **Type aliases** — `Scores = dict[str, list[int]]`, `X: TypeAlias = ...` (3.10+), or `type X = ...` (3.12+ syntax). An alias is just a name, not a new type (that is `NewType`).
- **`cast(T, v)`** — tells the checker "trust me"; at runtime it returns `v` untouched, no check, no conversion.
- **`Generic[T]`** — typed container classes (`Stack[int]`); 3.12 shortcut `class Stack[T]:`. `TypeVar("N", bound=Animal)` = that type or a subclass (subclass kept); `TypeVar("S", str, bytes)` = exactly one of the listed types.
- **`ParamSpec` + `Callable[P, R]`** (3.10+) — a decorator that keeps the wrapped function's parameter types. **`Self`** (3.11+) — methods returning "my own class". **`ClassVar`** — class-level attribute. **`NoReturn`/`Never`** — never returns normally.
- **Accept general, return specific** — parameters `Iterable`/`Sequence`/`Mapping` (callers can pass list, tuple, set, generator); return concrete `list`/`dict`.
- **Runtime access** — `fn.__annotations__` (raw), `typing.get_type_hints(fn)` (resolved), `get_origin`/`get_args`; validators, pydantic and FastAPI are built on this. `from __future__ import annotations` stores hints as strings (forward references need no quotes).
- **Running a checker** — `python -m pip install mypy`, then `mypy file.py` (`--strict` for more); or `pyright file.py`. Config in `pyproject.toml`.

## Gotchas (the part worth revising twice)
- Type hints are purely documentation/tooling — nothing stops `add("2", "3")` at runtime; don't rely on them as validation.
- `NewType` values print and behave identically to their base type at runtime — the distinction only exists for the type checker.
- `Any` silences all checking for that value (anything goes, may fail at runtime); `object` is the opposite — the strictest common type, forcing you to narrow before doing anything type-specific.
- Prefer the modern `X | None` / `list[int]` syntax (3.10+/3.9+) over `Optional[X]` / `List[int]` in new code — same meaning, no import needed.
- `cast`, `Generic[T]`, `bound=` and `ClassVar` are all checker-only: wrong code still runs, and fails later with an unrelated-looking error.
- `def f(x: list[int] = [])` shares ONE list across calls. Use `Optional[list[int]] = None`, then `if x is None:` — not `x = x or []`, which replaces a caller's legitimate empty list.
- Many type errors run fine (`age: int = "forty"`, returning `int` from `-> str`, `first_even(...) + 1` when it may be `None`) — only a checker reports them, so run one in CI.
- `from __future__ import annotations` must be the first statement of a module; afterwards `__annotations__` holds strings, so use `get_type_hints()` to read real types.

## When it matters
Larger codebases, public APIs, or anywhere a type checker (mypy/pyright) runs in CI to catch bugs before runtime — type hints turn implicit assumptions into checkable documentation.

## One-line recap example
```python
def greet(name: str | None = None) -> str:   # modern syntax, no import needed
    return f"Hello, {name or 'stranger'}"
```
