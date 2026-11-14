# Inspect, AST And Dis — Notes

## What this covers
How Python lets a program look inside itself: live objects (`inspect`, `types`), parsed source (`ast`), and the bytecode the interpreter runs (`dis`). This is the machinery under pytest, FastAPI, linters and debuggers.

## Key points
- **`inspect.signature(f)`** gives the parameters as data. Each `Parameter` has `.name`, `.kind`, `.default`, `.annotation`. Kinds: `POSITIONAL_ONLY`, `POSITIONAL_OR_KEYWORD`, `VAR_POSITIONAL` (`*args`), `KEYWORD_ONLY`, `VAR_KEYWORD` (`**kwargs`).
- **`sig.bind(...)`** checks a call without making it; `apply_defaults()` fills the omitted ones.
- **`getsource`, `getdoc`, `getmodule`, `getmembers(obj, predicate)`**; predicates `isfunction`, `isclass`, `ismethod`, `iscoroutinefunction`, `isgeneratorfunction`.
- **Who called me?** `inspect.currentframe().f_back.f_code.co_name`. `inspect.stack()` also works but is slow.
- **`functools.wraps`** keeps the original name, docstring and signature visible through a decorator (`__wrapped__`). Frameworks read signatures and type hints to build validation and CLIs automatically.
- **`types`**: `FunctionType`, `MethodType` (bind a function to one instance), `SimpleNamespace` (quick attribute bag), `ModuleType` (make a module with no file), `CodeType`.
- **Function internals**: `__code__.co_varnames / co_argcount / co_consts`, `__defaults__`, `__closure__[i].cell_contents` (proof closures keep live state).
- **`dis.dis(f)`** shows bytecode: `LOAD_FAST` (push a local), `LOAD_CONST` (push a constant), `BINARY_OP` (pop two, compute, push), `RETURN_VALUE`. Python folds constants (`60*60*24` becomes `86400` at compile time).
- **`ast.parse`** turns source into a tree **without running it**. `ast.dump(tree, indent=2)` prints it. `ast.walk` visits every node, `NodeVisitor` reads, `NodeTransformer` rewrites, `ast.unparse` turns the tree back into code.
- **`ast.literal_eval`** safely reads literals only: numbers, strings, lists, tuples, dicts, sets, `None`, booleans.
- **`compile(tree, name, "exec")` then `exec`** runs a (modified) tree.

## Gotchas (the part worth revising twice)
- **`getsource` can fail**: built-ins (`TypeError`), code made by `exec` or in the REPL (`OSError`). Always wrap it.
- **Bytecode differs between Python versions.** Print `dis` output to learn, never assert on it. Fewer instructions does not mean faster (a comprehension can show more instructions yet usually runs a bit faster).
- **`eval` runs anything** (`eval("__import__('os')...")`). Use `literal_eval` for data. It rejects even `1 + 2`, because arithmetic is code. It is not a shield against huge or deeply nested input.
- **Parsing is safe, `exec` is not.** Only `exec` code you trust.
- **After editing an AST** call `ast.fix_missing_locations(tree)` before `compile`.
- **A naive decorator** hides the real signature (`(*args, **kwargs)`). Always use `@functools.wraps`.
- **Mutable default arguments** are stored on the function (`f.__defaults__`), so every call shares them. You can literally see the list grow.
- **Frames hold references to all locals**, creating cycles. `del frame` when done.
- **`sys._getframe`, `__code__` internals and opcodes** are implementation details; prefer the public `inspect` API.
- **Mini linters are approximations**: an "unused import" check misses names used only in strings or `__all__`.

## When it matters
Writing frameworks, plugin loaders, test runners, serializers, CLI generators, linters and debuggers: code that must work on code it has never seen. In everyday business logic, peeking at callers, `hasattr` chains or `eval` on strings is usually a smell; a parameter, a Protocol or a dict of functions is the better design.

## One-line recap example
```python
import inspect
def area(w, h=10): return w * h
print(inspect.signature(area), [p.kind.name for p in inspect.signature(area).parameters.values()])
# (w, h=10) ['POSITIONAL_OR_KEYWORD', 'POSITIONAL_OR_KEYWORD']
```
