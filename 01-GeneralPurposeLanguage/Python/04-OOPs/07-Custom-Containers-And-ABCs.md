# Custom Containers & collections.abc — Notes

## What this covers
How to build your own list-like, dict-like and set-like classes: the container dunders (`__len__`, `__getitem__`, `__contains__`, `__iter__`, `__reversed__`, `__setitem__`, `__delitem__`), the `collections.abc` ABCs that give you many methods for free, and why subclassing `dict`/`list` directly can bite. ABC basics are in 05-Abstraction.py.

## Key points
- **Each feature calls one dunder**: `len()` -> `__len__`, `obj[i]` / `obj[a:b]` -> `__getitem__` (a slice arrives as a `slice` object), `x in obj` -> `__contains__`, `for` / `list()` / unpacking -> `__iter__`, `reversed()` -> `__reversed__`, `obj[i] = v` -> `__setitem__`, `del obj[i]` -> `__delitem__`.
- **ABCs = a shape + free methods**: you write the *abstract* methods, the ABC gives you the *mixin* methods built on top of them.
- **Which builtin is which**: `list` is a `MutableSequence`; `tuple`, `str`, `range` are `Sequence` (read-only); `dict` is a `MutableMapping`; `set` is a `MutableSet`; `frozenset` is a `Set`; a generator is an `Iterator` (not a `Collection`).
- **`Sequence`**: write `__getitem__` + `__len__` -> free `__contains__`, `__iter__`, `__reversed__`, `index`, `count`.
- **`MutableSequence`**: also write `__setitem__`, `__delitem__`, `insert` -> free `append`, `extend`, `pop`, `remove`, `reverse`, `clear`, `+=`. (`append` is just `insert(len, x)`.)
- **`Mapping` / `MutableMapping`**: write `__getitem__`, `__iter__`, `__len__` (+ `__setitem__`, `__delitem__`) -> free `get`, `keys`, `items`, `values`, `in`, `==`, `pop`, `popitem`, `clear`, `update`, `setdefault`. Put a rule (like `.lower()`) in the 3 core methods and every free method obeys it.
- **`Set`**: write `__contains__`, `__iter__`, `__len__` -> free `& | - ^ < <= > >= == isdisjoint`. Your constructor must accept an iterable (results are built with `cls(iterable)`). `add`/`discard` need `MutableSet`.
- **Slices and negatives are your job** in `__getitem__`: use `index.indices(len(self))` for slices, add `len` to negative ints, raise `IndexError` when out of range.
- **`UserList` / `UserDict` / `UserString`** wrap a real list/dict/str in `.data`; safe to subclass. Use `MutableSequence`/`MutableMapping` when your storage is not a plain list/dict.
- **Type hints**: accept the most general ABC (`Iterable[str]`, `Sequence[int]`, `Mapping[str, int]`), return a concrete type (`list[str]`). Hints are not enforced at runtime.

## Gotchas (the part worth revising twice)
- **Subclassing `dict`/`list` does not route through your overrides.** Override `__setitem__` on a `dict` subclass and the constructor, `update()` and `setdefault()` all bypass it. Same for `list.append` vs `extend`/`+=`/constructor, and `__getitem__` vs `.get()`. `UserDict` and `MutableMapping` route everything through `__setitem__`; `MutableSequence` routes `append`/`extend`/`+=` through `insert` (but `__setitem__` is separate). `UserList` still writes `.data` directly in `extend`.
- **`IndexError` is the "stop" signal.** The free `__iter__` and the old iteration fallback call `obj[0]`, `obj[1]`, ... until `IndexError`. A dict-style `__getitem__` raising `KeyError` makes `list(obj)` crash.
- **The old fallback**: a class with only `__getitem__` can be looped and used with `in`, but `isinstance(obj, Iterable)` is `False` and `reversed()` fails. The reliable "can I loop it" test is calling `iter()`.
- **Missing abstract method = `TypeError` at instantiation**, naming the missing methods (not at class definition, not at call time).
- **Not free anywhere**: `sort()`, `copy()`, `+`/`*` on sequences, a readable `__repr__`, and `==` for `MutableSequence`. Add them yourself or use `UserList`.
- **`Set` operator results follow the operand order**: `a & b` is built by looping over `b`, so the order comes from the right side. `Set` defines `__eq__`, so it is unhashable.
- **`str` is a `Sequence[str]`**: a function typed `Sequence[str]` accepts `"abc"` silently. Exclude `str`/`bytes` when dispatching with `isinstance(x, Iterable)`.
- **A generator is an `Iterable` but only once**: if you loop twice, take `Collection`/`Sequence` or do `items = list(items)`.
- `isinstance(x, Iterable[int])` raises `TypeError`; use bare `Iterable` at runtime.
- `isinstance(UserList(), list)` is `False` and `json.dumps` rejects it; unwrap `.data` when real built-in types are required.

## When it matters
Build on these ABCs when you need a custom collection (virtual/lazy sequence, case-insensitive dict, ordered set, a view over a file or DB) that works with `for`, `in`, `len`, slicing and every function expecting a standard container. Use the ABCs in signatures so callers can pass any compatible container.

## One-line recap example
```python
from collections.abc import Sequence

class Squares(Sequence):
    def __init__(self, n): self.n = n
    def __len__(self): return self.n
    def __getitem__(self, i):
        if not 0 <= i < self.n: raise IndexError
        return i * i

list(Squares(4)), 9 in Squares(4), Squares(4).index(9)   # ([0, 1, 4, 9], True, 3)
```
