# Dataclasses & Operator Overloading — Notes

## What this covers
`@dataclass` for auto-generating boilerplate (`__init__`, `__repr__`, `__eq__`) on data-holding classes, plus operator overloading — implementing dunder methods so custom objects work with `+`, `==`, `<`, `len()`, `in`, iteration, and more.

## Key points
- **`@dataclass`** auto-generates `__init__`, `__repr__`, and `__eq__` from type-annotated class fields — no need to hand-write them for simple data-holding classes.
- **Mutable defaults need `field(default_factory=list)`** instead of `= []` directly — dataclasses forbid a bare mutable default to avoid the shared-object bug (see 01-Functions.py, gotcha #19).
- **`@dataclass(frozen=True)`** makes instances immutable — attempting to assign to a field raises an error.
- **Operator overloading**: implement dunder methods to support built-in operators on custom classes — `__add__`/`__sub__`/`__mul__` for arithmetic, `__eq__`/`__lt__`/`__le__` for comparisons, `__len__`/`__contains__`/`__getitem__`/`__iter__` for container-like behavior (full container protocol: 07-Custom-Containers-And-ABCs.py).
- **`__post_init__`** runs automatically right after the generated `__init__` finishes — the place to validate input or compute fields derived from other fields.
- **`field(compare=False)`** excludes a field from the generated `__eq__`; **`field(repr=False)`** excludes it from `__repr__`.
- **`@dataclass(order=True)`** auto-generates `__lt__`/`__le__`/`__gt__`/`__ge__`, comparing fields in declaration order (like comparing tuples).
- **`@dataclass(slots=True)`** (3.10+) combines dataclass convenience with `__slots__` memory savings.
- **`__radd__`** is the fallback for `other + self` when `other`'s own `__add__` doesn't know how to handle your type (e.g. lets `sum([...])` work, since `sum` starts with `0 + first_element`). **`__iadd__`** backs in-place `+=`; without it, Python falls back to `__add__` (`a += b` becomes `a = a.__add__(b)`).
- **Unary operators**: `__neg__` (`-x`), `__pos__` (`+x`), `__abs__` (`abs(x)`), `__invert__` (`~x`). Return a new object. `__round__(ndigits=None)` backs `round()` (int back when no `ndigits`, same type back with it); `__trunc__`/`__floor__`/`__ceil__` back `math.trunc/floor/ceil`.
- **`__ne__` is free**: Python 3 derives `!=` from `__eq__` (just inverts it). Write `__eq__` only.
- **Return `NotImplemented`** from binary dunders (`__eq__`, `__add__`, `__lt__`...) when you don't understand `other`. Python then tries the other side's reflected method (`__radd__`, mirrored `__eq__`). If both give up: `+` raises `TypeError`, `==` falls back to identity.
- **Truthiness order**: `__bool__` first, then `__len__` (0 means False), else always True. `__bool__` must return a real `bool`.
- **`__format__(self, spec)`** backs `f"{obj:spec}"` and `format(obj, spec)`; you define what the spec string means. `!r`/`!s` convert first, then format.
- **`__repr__` vs `__str__` vs `__format__`**: repr = for programmers (always define it), str = for users (falls back to repr), format = custom specs (empty spec means `str(x)`).

## Gotchas (the part worth revising twice)
- **Dataclass inheritance field ordering**: fields from the base class come first, then the subclass's own fields — and a field WITHOUT a default cannot follow a field WITH a default in the combined list. If the base class has any defaulted field, every field the subclass adds must also have a default, or it's a `TypeError`.
- `@dataclass(frozen=True)` immutability is enforced through `__setattr__`, so attempts to mutate raise a normal exception you can catch — it's real enforcement, not just convention.
- `field(compare=False)` means two instances can be considered "equal" by `==` even when that field's actual values differ — easy to trip over if you forget which fields were excluded.
- `__radd__` should handle the identity-element case for `sum()`: `sum([...])` starts with `0 + first_element`, so `__radd__` needs an `if other == 0: return self` branch or `sum()` breaks.
- Defining `__iadd__` mutates the object in place — if you don't define it, `+=` silently falls back to `__add__` and creates a *new* object instead, which can be an important behavioral difference if other references to the original object exist.
- **Don't raise `TypeError` or return `False` for an unknown type** in a binary dunder. Raising kills the operation before the other side is asked; `False` claims "definitely not equal" so the other side never votes. Return `NotImplemented`. (Right operand being a subclass is tried first.)
- `Meters(1) == "x"` is just `False` (not an error) because both sides return `NotImplemented` and Python falls back to identity; `Meters(1) + "x"` is a `TypeError` for the same reason.
- A class with `__len__` but no `__bool__` is falsy when empty; if both exist `__bool__` wins. `if not x` can't tell `None` from `[]` — use `is None`.
- `f"{obj:>10}"` raises `TypeError` unless you define `__format__` (default only accepts an empty spec). `!s` first (`f"{obj!s:>10}"`) is the quick workaround.
- `__eq__` without `__hash__` makes the class unhashable (details in 04-Polymorphism.py).

## When it matters
Use `@dataclass` for any class that's mostly a bag of related fields (records, DTOs, config objects) — reach for operator overloading when a custom type (vectors, money, versions) should behave naturally with `+`, `==`, `<`, sorting, or iteration instead of exposing awkward method calls.

## One-line recap example
```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: int
    y: int

Point(2, 3) == Point(2, 3)   # True - auto-generated __eq__
```
