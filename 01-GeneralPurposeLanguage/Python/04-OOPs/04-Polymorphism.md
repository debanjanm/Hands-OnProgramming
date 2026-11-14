# Polymorphism — Notes

## What this covers
"Many forms" — the same method name or operator behaving differently depending on the object it's used with. Covers method overriding, duck typing, callable objects, and comparison-related dunder methods.

## Key points
- **Polymorphism** = the same operation (method call, operator) behaves differently depending on the actual type of the object — `len()` and `+` already do this for built-in types.
- **Via inheritance/overriding**: a shared method name (`speak()`) defined differently in each subclass — calling `animal.speak()` in a loop runs the right version for whatever type `animal` actually is.
- **Duck typing**: Python doesn't require a common base class — any object with the right method/attribute works ("if it walks like a duck and quacks like a duck..."). A function can accept anything with a `.speak()` method, no shared `Animal` ancestor needed.
- **`__call__`**: defining it lets instances be invoked like functions (`obj(value)`) — the same call syntax works for functions, lambdas, and objects alike.
- **`functools.singledispatch`**: one function with different implementations chosen by the *type* of its first argument — polymorphism resolved by argument type rather than by which object's method runs.
- Operator overloading (`__add__`, `__eq__`, etc., detailed in 06-Dataclasses-And-Operator-Overloading.py) is polymorphism too — it lets `+`/`==`/`<` "do the right thing" for custom objects.
- ABCs (see 05-Abstraction.py) can force subclasses to implement a shared method, guaranteeing polymorphism works consistently across all of them.

## Gotchas (the part worth revising twice)
- **`__eq__` and `__hash__` are linked**: by default, objects are hashable (by `id()`) and compared by identity. The moment you override `__eq__` to compare by value, Python automatically sets `__hash__` to `None` — the object becomes unhashable (can't go in a `set` or be a dict key) unless you also define `__hash__` explicitly, consistent with your `__eq__`.
- **`functools.total_ordering`**: writing all of `__lt__`, `__le__`, `__gt__`, `__ge__` by hand is repetitive — define `__eq__` plus just ONE of the others, and `@total_ordering` fills in the rest.
- Duck typing means there's no compile-time or import-time check that an object has the right method — mismatches only surface as an `AttributeError` at call time.
- `singledispatch` dispatches on the type of the *first argument only*, and falls back to the generic (undecorated) implementation for any type without a registered overload.

## When it matters
Reach for polymorphism whenever you want one function/loop to work uniformly across several types now, and to keep working when new types (e.g. a new `Bird` class) are added later, without touching the existing code.

## One-line recap example
```python
animals = [Dog(), Cat()]
for animal in animals:
    print(animal.speak())   # same call, different behavior per actual type
```
