# Behavioral Design Patterns — Notes

## What this covers
How objects communicate and share work: Strategy (class vs plain function), Observer/event emitter, Command with undo, State, Template Method, Iterator, Chain of Responsibility, Visitor (classic and `singledispatch`), Mediator, Memento, and Null Object. Each one is shown with its Pythonic shortcut and a "when NOT to use" note.

## Key points
- **Strategy**: swap one way of doing a job for another. In Python just pass a function (`sorted(key=len)` is Strategy). Use a class only if the strategy has its own state.
- **Observer**: a source keeps a list of callbacks and calls them on an event. Callbacks are plain callables; a small `on/off/emit` class is enough.
- **Command**: an action as an object with `execute()` and `undo()`. A history stack gives undo. Without undo, a function or `functools.partial` does the same job.
- **State**: behavior depends on the current mode. Use state objects for rich behavior, or a `{(state, event): next_state}` dict for simple machines.
- **Template Method**: the base class fixes the steps; subclasses fill in the blanks. If only one step varies, pass a function instead.
- **Iterator**: already built in (`__iter__`/`__next__`). Write a generator with `yield` instead of a class.
- **Chain of Responsibility**: a request passes through handlers until one answers. A list of functions plus a loop is enough (middleware style).
- **Visitor**: add new operations to stable classes. Classic form uses `accept()`; `functools.singledispatch` or `match` is simpler and works on classes you don't own.
- **Mediator**: many-to-many talk goes through one hub, so objects don't know each other.
- **Memento**: save a snapshot of state and restore it later. A frozen dataclass or `copy.deepcopy` works.
- **Null Object**: a do-nothing object with the same methods, so callers skip `if x is not None` checks. `contextlib.nullcontext` is a stdlib example.

## Gotchas (the part worth revising twice)
- A **generator is used up** after one pass; a container with a generator `__iter__` can be looped many times because each loop makes a fresh generator.
- In Observer, loop over a **copy** of the handler list; otherwise a handler that unsubscribes mid-emit skips the next handler.
- Memento with a **shallow copy** shares inner lists/dicts with the live object, so later changes leak into the "snapshot". Use `deepcopy` or immutable data.
- `singledispatch` only looks at the **first argument's type**. For two-argument dispatch it will not help.
- A Mediator that holds all the logic becomes a **god object**; keep it to routing.
- Null Object can **hide bugs**: if "missing" is truly an error, fail loudly instead.
- Template Method pushes you toward **inheritance**; deep hierarchies get rigid. Prefer passing callables.
- Patterns are for pain relief, not decoration. One or two variants rarely need Strategy or State classes.

## When it matters
Reach for these when plain code starts to hurt: growing `if/elif` chains (Strategy, State), one event with many reactions (Observer), the need to undo or queue actions (Command, Memento), or adding operations across a stable class family (Visitor). They also give you shared vocabulary for code reviews and reading other people's code.

## One-line recap example
```python
# Strategy the Pythonic way: the "strategy" is just a function
print(sorted(["pear", "fig", "banana"], key=len))  # ['fig', 'pear', 'banana']
```
