# Control Flow — Notes

## What this covers
How Python decides what runs and how many times: `if`/`elif`/`else` branching, `for`/`while` loops, `break`/`continue`, plus newer additions like `match-case` and `zip(strict=True)`.

## Key points
- `if` / `elif` / `else`: only one branch runs — first true condition wins.
- `for` loops iterate over any iterable (list, string, range, etc.); `while` loops run as long as a condition stays true.
- Both `for` and `while` support an `else` clause — it runs only if the loop finished normally (no `break`).
- `break` exits the loop immediately; `continue` skips to the next iteration.
- `match-case` (3.10+) is a structural pattern matcher — it can unpack tuples/lists, bind variables, use `|` for multiple values, and add `if` guards. `case _:` is the wildcard/default.
- Ternary expressions (`a if cond else b`) can be chained for 2-3 branch decisions.
- `any()`/`all()` short-circuit — they stop as soon as the answer is known.
- `zip(a, b, strict=True)` (3.10+) raises `ValueError` if the iterables have different lengths, instead of silently truncating.
- `range()` is lazy (constant memory); `list(range(...))` eagerly builds the whole list — only do that if you actually need list operations.

## Gotchas (the part worth revising twice)
- Python has no `break 2` / labeled loops for nested loops. Workarounds: a flag variable, wrapping in a function and using `return` (cleanest), or `itertools.product()` to flatten nested loops into one.
- The loop `else` is confusing at first — it means "didn't break," not "loop ran."
- Default `zip()` silently stops at the shortest iterable, which can hide real bugs — use `strict=True` when lengths must match.
- Don't wrap `range()` in `list()` just to loop over it — it's already iterable and lazy; only materialize it if you need indexing/slicing/mutation.

## When it matters
Every program needs this — branching for decisions, loops for repetition. `match-case` is worth reaching for over long `if/elif` chains when you're checking a value's shape/structure, not just its value.

## One-line recap example
```python
for i in range(5):
    if i == 3:
        break
    print(i)
else:
    print("only runs if the loop was never broken")
```
