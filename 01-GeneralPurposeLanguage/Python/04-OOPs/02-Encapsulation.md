# Encapsulation — Notes

## What this covers
Bundling data and behavior together and controlling access to it: public vs private instance variables, getters/setters via `@property`, static variables/methods, attribute-access magic methods, and aggregation.

## Key points
- **Encapsulation** = wrapping data and the methods that operate on it into one unit (a class), plus data hiding — preventing direct outside access and forcing access through defined methods.
- **Public** instance variables (default) are accessible from anywhere. **Private** ones use a `__` prefix (e.g. `self.__student_id`) — Python renames these via name mangling to discourage direct outside access.
- **Getters/setters**: the Pythonic way is `@property` (getter) and `@name.setter` (setter) — lets you validate input while callers still use plain attribute syntax (`product.price = 120`).
- **Instance variables** are unique per object; **static/class variables** are shared by all instances and typically accessed via the class name.
- **`@staticmethod`**: belongs to the class conceptually but takes no implicit `self`/`cls` — just a utility function namespaced inside the class.
- **Attribute-access magic methods**: `__getattr__` (called when normal lookup fails), `__setattr__` (called on every assignment), `__delattr__` (called on deletion) — give you fine control over how attributes behave.
- **Aggregation** = a "has-a" relationship where the contained ("part") object can exist independently of the container ("whole") — e.g. an `Employee` has an `Address`, but the `Address` object is fine on its own.
- **`functools.cached_property`**: like `@property` but computes the value once and caches it in the instance's `__dict__` — later accesses skip recomputation.

## Gotchas (the part worth revising twice)
- **Name mangling is not real privacy**: `self.__balance` inside `class Account` gets rewritten to `self._Account__balance`. It exists to avoid accidental name clashes in subclasses — it is still visible in `vars()`/`__dict__` and still reachable from outside if you know the mangled name.
- **Python's privacy is "we're all consenting adults here"**: a single underscore `_attr` is purely a convention ("internal, please don't touch") — nothing in the language enforces it, unlike `private` in Java/C++. Nothing stops `account._balance = 999999` from outside.
- **`__slots__` + `@property` combo**: the property's backing attribute (e.g. `_radius`) must ALSO be listed in `__slots__`, since there's no `__dict__` left to fall back on for storage.
- `__getattr__` is only called when normal attribute lookup *fails* — it won't fire for attributes that already exist directly on the instance. `__setattr__`, by contrast, fires on *every* assignment, so custom implementations must special-case internal attributes (like the mangled `__data`) to avoid infinite recursion.
- `cached_property` only makes sense for values that don't change after first computation — staleness is the tradeoff for skipping recomputation.

## When it matters
Use encapsulation whenever a class holds data that needs validation, controlled mutation, or a stable public interface while the internal representation is free to change later.

## One-line recap example
```python
class Product:
    def __init__(self, price):
        self.__price = price
    @property
    def price(self):
        return self.__price
    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self.__price = value
```
