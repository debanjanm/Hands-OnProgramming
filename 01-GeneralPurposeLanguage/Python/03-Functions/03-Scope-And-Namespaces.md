# Scope & Namespaces — Notes

## What this covers
The full mental model behind "where does this name live?": namespaces, the LEGB lookup rule, `global`/`nonlocal`, shadowing, closures in loops, class-body quirks and why mutable globals hurt. It is the explanation behind most `NameError` / `UnboundLocalError` bugs.

## Key points
- **Namespace** = a name -> object mapping (a real `dict` in CPython). **Scope** = the region of code where that mapping is directly visible. Every `x = ...`, `def`, `class`, `import` just adds a key.
- **`globals()`** is the module's dict (writing to it creates variables). At module level `locals()` **is** `globals()`. Inside a function, `locals()` is a snapshot copy.
- Modules, classes and instances each own a namespace in `__dict__`. A class `__dict__` is a read-only `mappingproxy`. `obj.name` searches instance -> class -> bases.
- **LEGB** lookup, innermost first: **L**ocal -> **E**nclosing functions -> **G**lobal (module) -> **B**uilt-in. No hit = `NameError`.
- **Local is decided at compile time**: any name assigned anywhere in a function body is local in the whole function (visible in `co_varnames`). Global vs built-in is resolved at run time.
- **`global x`** lets a function *rebind* a module-level name (and can create a new one). **`nonlocal x`** rebinds a name in the nearest enclosing *function*; the name must already exist and it can never reach globals.
- **Mutating is not rebinding**: `log.append(...)`, `d[k] = v`, `state.count += 1` on an object need no `global`. Only `name = ...` does.
- **Only `def`, `class`, `lambda`, comprehensions and modules create scopes.** `if`/`for`/`while`/`with`/`try` do not.
- **Built-ins** are attributes of the `builtins` module. Import `builtins` instead of relying on `__builtins__`.
- **`del name`** removes the binding, not the object; the object is freed when nothing refers to it (CPython refcount). `except ... as e` auto-deletes `e` at the end of the block.
- **`types.SimpleNamespace`** is a tidy attribute bag (`ns.port` instead of `d["port"]`); good for config.
- **Prefer** parameters and return values over module-level state; UPPER_CASE constants are fine.

## Gotchas (the part worth revising twice)
- **`UnboundLocalError`**: `counter = counter + 1` inside a function fails, because assigning makes `counter` local for the *entire* function, so the right-hand side reads an empty local. Even `if False: total = 0` is enough to make `total` local. Fix: `global counter`, or (better) pass in and return the value.
- **`max = max(a, b)` inside a function** is the same trap — it also shadows the built-in.
- **Shadowing built-ins is silent**: `list = [1]`, `sum = 10`, `id = "user-7"` make the built-in unreachable (`TypeError: 'int' object is not callable`). Recover with `del name` or `builtins.name`.
- **Late-binding closures**: `[lambda: i for i in range(3)]` all return `2`, because the closure captures the *variable*, not its value, and reads it when called. Fixes: default argument `lambda i=i: i` (callers can override it), `functools.partial`, or a factory function.
- **Class bodies are not enclosing scopes**: a method using bare `LIMIT` gets `NameError` — use `self.LIMIT` or `Config.LIMIT`. In a class-body comprehension only the *first* iterable sees class names; a condition using `LIMIT` fails (still true in 3.12 even though comprehensions are inlined).
- **Loop variables leak out of `for`** (they stay defined after the loop, but not if the loop never ran) while comprehension variables do **not** leak. The walrus `:=` inside a comprehension *does* bind in the enclosing scope.
- **`locals()` in a function is a copy**: writing to it changes nothing real.
- **`except ... as err`** deletes `err` afterwards — save it to another name if you need it later.
- **Names set only under `if __name__ == "__main__":` don't exist on import**, so functions reading them crash when imported. Pass values in explicitly.
- Mutable globals give hidden inputs: same call, different answer, hard to test. Let an object own its state instead.
- Injecting into `builtins` works everywhere but is a terrible idea outside experiments.

## When it matters
Whenever you see `NameError`, `UnboundLocalError`, a variable that changed "by itself", closures made in a loop (callbacks, buttons, threads), or a mysterious "not callable" on a built-in. Understanding it makes closures, decorators and `nonlocal` easy.

## One-line recap example
```python
counter = 10
def bad():
    counter = counter + 1      # UnboundLocalError: counter is local for the whole function
def good(value):
    return value + 1           # pass in, return out - no global needed
counter = good(counter)
```
