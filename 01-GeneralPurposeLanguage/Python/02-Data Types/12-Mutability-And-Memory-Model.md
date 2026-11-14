# Mutability and Memory Model — Notes

## What this covers
How Python really stores data: names pointing at objects, mutable vs immutable, aliasing, copying, argument passing, reference counting, the garbage collector, weak references, and how to measure memory.

## Key points
- **Names are labels, not boxes.** `b = a` never copies; it puts a second label on the same object. `is` compares identity (`id`), `==` compares value.
- **Mutable** (change in place, same id): list, dict, set, bytearray, most class instances. **Immutable** (never change): int, float, str, tuple, frozenset, bytes, None. "Changing" an immutable builds a new object and rebinds the name.
- **Mutate vs rebind**: mutating an object (`a.append`) is seen by every name on it; rebinding a name (`a = [...]`) moves only that name.
- **Containers store references.** `seq * n` and shallow copies share the inner objects.
- **`x += y`**: in place for lists (`__iadd__`, same id); rebinding for int, str, tuple (new id). `x = x + y` on a list builds a new list.
- **Argument passing = pass by object reference.** The parameter is a new name for the caller's object. Mutating it shows outside; rebinding it does not.
- **Reference counting (CPython)**: an object is freed the moment its count hits 0. `sys.getrefcount(x)` is always 1 higher than you expect (the argument itself).
- **`del name`** removes a label, not the object. The object dies only when the last reference goes.
- **Cyclic GC** (`gc`): finds groups of objects that only reference each other. `gc.collect()` forces it; `gc.get_threshold()` / `gc.get_count()` show how it triggers.
- **`weakref`**: a reference that does not keep the object alive (returns `None` after death). `WeakValueDictionary` is a self-cleaning cache.
- **Copying**: shallow = `a[:]`, `a.copy()`, `list(a)`, `copy.copy(a)` (new outer, same inner). `copy.deepcopy(a)` copies everything and handles cycles.
- **Sizing**: `sys.getsizeof` is shallow (container only). Walk the structure recursively (with a `seen` set) for the true size. `tracemalloc` shows real allocations by line.
- **Generators vs lists**: 100k ints in a list cost about 3.8 MB; a generator over the same values needs under 1 KB.

## Gotchas (the part worth revising twice)
- `backup = original` is not a backup. Use `.copy()` (or `deepcopy` for nested data).
- `[[0]*3]*3` makes three references to ONE row. Use `[[0]*3 for _ in range(3)]`. `[0]*3` alone is fine (ints are immutable). Same trap: `dict.fromkeys(keys, [])`.
- `t = ([1],); t[0] += [2]` raises `TypeError` **and** changes the list: the in-place add works, then storing back into the tuple fails. `t[0].extend([2])` is clean.
- A tuple is only shallowly immutable: it can hold a list that changes. Such a tuple is unhashable.
- `lst += x` accepts any iterable; `lst + x` needs a list. With aliases, `+=` is visible to others, `lst = lst + x` is not.
- Mutable default argument (`def f(x, bag=[])`) is created once and shared by all calls. Default to `None` instead.
- Reference cycles are not freed by refcounting alone; only `gc` frees them, and not instantly.
- You cannot weakref an `int`, `str`, `list`, `dict`, `tuple`. A subclass or normal class instance works. A `__slots__` class needs `'__weakref__'` in its slots.
- `__del__` is not a reliable cleanup hook (may run late or never). Use `with`, `try/finally`, or `weakref.finalize`.
- Never compare numbers or strings with `is`; small-int and string interning is a CPython detail.
- `sys.getsizeof([big_obj]*1000)` says nothing about the big objects. Shared objects must be counted once.

## When it matters
Any time data "changes by itself" (aliasing), when you pass lists or dicts into functions, when copying nested config or grids, when writing caches, and when a program uses too much memory.

## One-line recap example
```python
a = [[0] * 2] * 2          # two references to the same row
a[0][0] = 1
print(a)                   # [[1, 0], [1, 0]]  <- shared row; use a comprehension to fix
```
