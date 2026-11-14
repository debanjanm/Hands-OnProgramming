# Built-in Functions — Notes

## What this covers
A guided tour of the functions Python gives you with no import: output/input, numbers, sequences, types, introspection, text, running code, and the `builtins` module itself. Knowing them well means shorter, faster code (they are written in C).

## Key points
- **Where they live**: the `builtins` module. Name lookup is Local -> Enclosing -> Global -> **Built-in**, so `len` is found last.
- **`print(*values, sep=" ", end="\n", file=sys.stdout, flush=False)`**: `sep` goes between values, `end` after the last, `file` can be any object with `.write()`. It **returns `None`**.
- **`input()`** always returns a `str`, even for digits — convert with `int()`/`float()` yourself. Empty stdin raises `EOFError`.
- **`str` vs `repr`**: `str` is for users (what `print` shows), `repr` is for developers (unambiguous, quotes included, used inside lists). `ascii()` is `repr` with non-ASCII escaped. `format(x, spec)` = `f"{x:spec}"`.
- **Numbers**: `abs`, `round`, `divmod(a, b)` = `(a // b, a % b)`, `pow(b, e, m)` = modular power (fast even for huge numbers; `pow(3, -1, 7)` is a modular inverse).
- **`sum(iterable, start=0)`**, **`min`/`max`** accept `key=` (how to compare) and `default=` (value for an empty input).
- **Conversions**: `int("ff", 16)`, `int("0b11", 0)` (base 0 reads the prefix), `bin/hex/oct` return **strings**, `float`, `bool`, `complex`.
- **Sequences**: `len`, `range` (lazy: stores only start/stop/step), `enumerate(x, start=1)`, `zip`, `reversed`, `sorted`, `iter`, `next(it, default)`, `slice`.
- **`map` / `filter`** are lazy and single-use; `filter(None, data)` keeps truthy items.
- **`any` / `all`** short-circuit. `any([])` is `False`, `all([])` is `True` (vacuous truth).
- **Types**: `type`, `isinstance(x, (int, float))`, `issubclass`, `id`, `hash`, `callable`. Prefer `isinstance` over `type(x) == T` (it respects inheritance).
- **Introspection**: `dir`, `vars` (an instance's `__dict__`), `globals`, `locals`, and `getattr/setattr/hasattr/delattr` for attributes held in strings.
- **Text**: `ord("A")` -> 65, `chr(65)` -> `"A"`. Methods like `upper`/`split` are **not** built-ins — they belong to `str`.
- **Code execution**: `eval` (one expression), `exec` (statements), `compile` (turn text into a code object once).
- **Misc**: `open`, `__import__` (what the `import` statement calls), `breakpoint()` (drops into `pdb`; `PYTHONBREAKPOINT=0` disables it), `help`.
- **Not all "functions" are functions**: `int`, `str`, `list`, `zip`, `map`, `range`, `enumerate` are really **classes** you call like functions.

## Gotchas (the part worth revising twice)
- **`round()` uses banker's rounding**: exact halves go to the nearest even number (`round(2.5)` is 2, `round(3.5)` is 4). Also `round(2.675, 2)` gives 2.67, because the float is really 2.67499... For school-style rounding use `Decimal(...).quantize(..., ROUND_HALF_UP)`.
- **`zip` stops at the shortest input silently** — extra items vanish. Use `itertools.zip_longest` or `zip(..., strict=True)` (3.10+) if lengths must match.
- **`sum` of floats accumulates error** (`sum([0.1]*10)` is not 1.0); `math.fsum` fixes it. `sum` of strings fails — use `"".join(...)`. `sum(list_of_lists, [])` works but is O(n²).
- **`max([])` raises `ValueError`** unless you pass `default=`. On ties, `min`/`max` return the **first** winner.
- **`int(-4.9)` is -4** (truncates toward zero), `divmod(-7, 2)` is `(-4, 1)` (floors). `int("4.2")` fails — go through `float` first.
- **`bool("0")` is `True`** (non-empty string). **`nan != nan`** — use `math.isnan`.
- **`isinstance(True, int)` is `True`**: `bool` is a subclass of `int`.
- **`nums.sort()` sorts in place and returns `None`**; `sorted(nums)` returns a new list. `sorted([3, "a"])` raises `TypeError`.
- **`map`/`filter`/`zip`/`reversed` objects are single-use** — iterate twice and the second pass is empty. `reversed()` needs a sequence (a generator fails).
- **`eval`/`exec` on untrusted text = arbitrary code execution.** Emptying `__builtins__` is a leaky sandbox, not protection. For data use `ast.literal_eval` or `json.loads`.
- **`hash()` of a `str` is randomised per process** — never store it in a file. Lists/dicts/sets are unhashable (so not valid dict keys).
- **Shadowing a built-in is silent**: `list = [1]` or `sum = 0` makes the built-in unreachable in that scope (`list("abc")` -> `TypeError`). Fix: pick another name, or `del name` to reveal the built-in again. Linters flag it.
- `print` returns `None`, and `hasattr` only swallows `AttributeError` — `getattr(obj, name, default)` is often cleaner.

## When it matters
Almost every line you write uses these. Reach for `enumerate`, `zip`, `sorted(key=...)`, `any/all`, `min/max(key=...)` before writing a manual loop. Revisit the gotchas when numbers look "off" (rounding, floats) or a built-in suddenly says `not callable` (shadowing).

## One-line recap example
```python
words = ["pear", "fig", "banana"]
print(max(words, key=len), list(enumerate(words, 1)), round(2.5), any(w.startswith("f") for w in words))
# banana [(1, 'pear'), (2, 'fig'), (3, 'banana')] 2 True
```
