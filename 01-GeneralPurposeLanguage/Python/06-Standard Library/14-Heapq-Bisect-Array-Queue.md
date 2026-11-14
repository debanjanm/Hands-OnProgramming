# Heapq, Bisect, Array and Queue — Notes

## What this covers
Four small stdlib toolkits for picking the right data structure: `heapq` (smallest-first), `bisect` (sorted-list search), `array` (compact numbers) and `queue` (thread-safe hand-off of work). Includes a "which structure for which job" cheat table.

## Key points
- **`heapq`** turns a plain list into a **min-heap**: `heap[0]` is always the smallest. `heappush` / `heappop` are O(log n), peeking is O(1), `heapify(list)` is O(n).
- `heappushpop(h, x)` = push then pop. `heapreplace(h, x)` = pop then push (so it can return something bigger than `x`).
- `nlargest(k, data, key=...)` / `nsmallest` give top-K without sorting everything. For `k == 1` use `min`/`max`; for `k` near `n` just `sorted()`.
- **Max-heap**: push negated numbers, negate again when you pop.
- `heapq.merge(*sorted_inputs)` lazily merges already-sorted streams — works on data too big for memory.
- **Priority queue recipe**: push `(priority, counter, item)`. The counter is unique, so ties never compare the item and equal priorities stay first-in-first-out.
- **Lazy deletion**: don't remove from the middle (O(n)); mark the entry dead and skip it when it surfaces. Also how you "change priority".
- **Top-K of a stream**: keep a min-heap of size K, `heapreplace` when a new value beats `heap[0]`. Memory stays O(K).
- **`bisect`** does binary search (O(log n)) on a **sorted** list. `bisect_left` = insert before equals, `bisect_right` = insert after equals.
- `insort` inserts and keeps order. `key=` works on Python 3.10+.
- Neat uses: fast membership test on a sorted list, grade/tax-bracket lookup with `bisect_right(breakpoints, score)`.
- **`array.array(typecode, ...)`** stores raw machine numbers of ONE type (`'i'`, `'h'`, `'d'`, `'B'`...). About 8x less memory than a list of ints for 1000 numbers.
- `tobytes()/frombytes()` and `tofile()/fromfile()` give fast binary save/load.
- **`queue`**: `Queue` (FIFO), `LifoQueue` (stack), `PriorityQueue` (smallest first), `SimpleQueue` (minimal, unbounded). They handle the locking and waiting for you.
- `maxsize` makes `put()` block when full — back-pressure so a fast producer can't flood memory.
- `put_nowait` / `get_nowait` raise `queue.Full` / `queue.Empty`; `put/get(timeout=...)` wait a bit then raise.
- `task_done()` after finishing each item + `q.join()` = "wait until all work is really done".
- **Clean worker shutdown**: put one sentinel (e.g. `None`) per worker.
- `collections.deque` is the O(1) FIFO for single-thread code (`popleft`), see `01-Collections-Module.py`.

## Gotchas (the part worth revising twice)
- `heapq` is **min-only**; and only `heap[0]` is guaranteed smallest — `heap[1:]` is NOT sorted.
- `heappush(h, (1, {...}))` twice with the same priority raises `TypeError` (it tries to compare the dicts). Add the counter.
- `bisect` on an unsorted list gives silent nonsense, no error.
- `insort` finds the spot in O(log n) but the list shift makes it O(n) overall. Millions of inserts -> use a heap or a tree library.
- `array` rejects the wrong type (`TypeError`) and out-of-range values (`OverflowError`). Byte order is machine-specific, so don't share raw files across machines blindly.
- `sys.getsizeof(a_list)` ignores the int objects inside it — add them up for a fair comparison.
- `qsize()`, `empty()`, `full()` are only snapshots under threads. Catch `Empty`/`Full` instead of "check then act".
- If anyone calls `join()`, every `get()` must be matched with a `task_done()` — or `join()` hangs forever.
- Thread output order is not deterministic; collect results and sort before printing/comparing.

## When it matters
Schedulers and job runners (priority queue), "top 10 of a huge log" (heap), range/bucket lookups (`bisect`), big numeric buffers or binary files (`array`), and any producer/consumer pipeline with worker threads (`queue`).

## One-line recap example
```python
import heapq
h = []; [heapq.heappush(h, x) for x in (5, 1, 3)]
print(heapq.heappop(h))   # 1  -> smallest always comes out first (min-heap)
```
