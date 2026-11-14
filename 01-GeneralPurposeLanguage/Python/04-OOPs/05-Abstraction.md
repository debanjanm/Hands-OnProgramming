# Abstraction — Notes

## What this covers
Hiding implementation complexity behind a simple interface — the difference from encapsulation, and using `abc.ABC`/`@abstractmethod` to actually enforce that subclasses implement required methods.

## Key points
- **Abstraction** hides *how* something works and exposes only *what* it does (e.g. driving a car: you use the steering wheel/pedals, not the engine internals). This is different from **encapsulation**, which hides *data*.
- Without enforcement, a base class method that's just `pass` doesn't force subclasses to override it — a forgotten override silently does nothing until it's called and causes a bug.
- **`ABC` + `@abstractmethod`** (from the `abc` module) fixes this: the abstract class can't be instantiated directly, and any subclass missing a required method also can't be instantiated.
- Abstract classes can still have **concrete (shared) methods** alongside abstract ones — subclasses get the shared logic for free while being forced to fill in the abstract parts.
- **`ABC.register(SomeClass)`**: makes `SomeClass` count as a "virtual subclass" for `isinstance()`/`issubclass()` checks, without any real inheritance — useful for retrofitting an interface onto a class you don't control.
- Stacking `@property` above `@abstractmethod` forces subclasses to expose the member as a *property* (attribute-style access), not a plain method call.
- **`typing.Protocol`** is structural typing — any class with matching methods satisfies the protocol automatically, no inheritance or registration needed (contrast with ABC's nominal typing, which requires an explicit `is-a` declaration).

## Gotchas (the part worth revising twice)
- **This is deliberate fail-fast design**: without ABC, a missing method surfaces only when it's called (possibly deep in production, much later). With ABC, the `TypeError` happens the moment you try to instantiate the incomplete class — far cheaper to debug.
- `Flyer.register(Airplane)` makes `isinstance(plane, Flyer)` return `True` and `issubclass(Airplane, Flyer)` return `True`, but `Flyer` is NOT in `Airplane.__mro__` — there's no real inheritance link, no shared code, no MRO change. It's purely a registered relationship for type-checking purposes.
- ABC = nominal typing (must explicitly inherit or register to "count"). Protocol = structural typing (matching shape is enough). Don't confuse the two — `isinstance()` against a plain `Protocol` only works if it's marked `@runtime_checkable`.
- An abstract class can still define `__init__` and other regular methods — "abstract" only blocks instantiation of the class itself and requires the specific `@abstractmethod`-marked methods to be overridden, not the whole class to be rewritten.

## When it matters
Use ABC when you're designing a shared interface that multiple implementations must honor (payment methods, shape types, notification channels) and you want a hard guarantee — not just a comment — that every implementation provides the required methods.

## One-line recap example
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...

# Shape() -> TypeError: can't instantiate abstract class
```
