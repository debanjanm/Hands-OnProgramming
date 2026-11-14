# Modules and Packages — Notes

## What this covers
How Python organizes code across files (modules) and folders (packages) — different import styles, your own local packages, and how the import system actually behaves under the hood.

## Key points
- A **module** is a single `.py` file. A **package** is a directory of modules, historically marked with `__init__.py`.
- Import styles: `import math`, `import math as m`, `from math import sqrt`, `from math import pi as PI`.
- `from module import *` pulls all public names into the current namespace — generally discouraged since it's unclear where a name came from and risks clashes.
- `dir(module)` lists a module's contents, useful for exploring what's available.
- `__name__ == "__main__"` idiom: code under this guard only runs when the file is executed directly, not when imported — every module has a `__name__` that's `"__main__"` only when run directly.
- `__all__ = [...]` at module level explicitly controls what `import *` pulls in; anything not listed is skipped by `*` (but still reachable via a normal dotted import).
- Relative imports inside a package use leading dots: `from . import sibling_module` (current package), `from .. import x` (parent package) — only valid inside a package, never in a script run directly.
- `importlib.import_module("name")` imports a module by string name, useful when the module name is only known at runtime (config/plugin systems).
- Namespace packages (PEP 420, 3.3+): a directory **without** `__init__.py` can still act as a package, letting one logical package span multiple directories/distributions.
- Standard library (ships with Python) vs third-party (installed via `pip`) vs local (your own project code) — three sources of importable modules.

## Gotchas (the part worth revising twice)
- **Module caching via `sys.modules`**: a module's top-level code runs only the FIRST time it's imported anywhere in the program. Every later import (even via a different path/alias, or via `importlib`) reuses the same cached module object — no re-execution, no repeated side effects.
- A directly-run script's own folder is automatically added to `sys.path`, which is why a sibling package/folder is importable without extra setup — but this only applies to the *entry-point* script, not to modules imported deeper in the chain.
- `__all__` only affects `from module import *` — it does NOT make other names private or block a normal `from module import _private_thing`.

## When it matters
Any project beyond a single script needs this — splitting code into modules/packages keeps things organized, and understanding import caching/relative imports avoids confusing "why did my print statement not run again" or "attempted relative import" errors.

## One-line recap example
```python
from demo_package.math_utils import add   # explicit import of one name

print(add(2, 3))   # 5 — demo_package's __init__.py already ran once, cached in sys.modules
```
