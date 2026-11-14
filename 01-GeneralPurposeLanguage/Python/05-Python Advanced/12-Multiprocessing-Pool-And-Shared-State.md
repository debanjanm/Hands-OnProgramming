# Multiprocessing: Pools and Shared State — Notes

## What this covers
How to use several processes for real CPU parallelism: start methods, `Pool` and `ProcessPoolExecutor`, what can be pickled, the cost of copying data, and the ways processes can share state (`Value`, `Array`, `SharedMemory`, `Manager`, queues, pipes).

## Key points
- **Why processes**: each has its own interpreter, GIL and memory, so CPU-bound Python really runs in parallel. Costs: slow start (a process is much slower to start than a thread) and everything crossing the boundary is **pickled (copied)**.
- **Start methods**: `spawn` (fresh interpreter that *re-imports your file*; default on macOS/Windows), `fork` (clone the parent; fast but unsafe with threads), `forkserver` (clean helper forks children; Python 3.14 default on Linux). `set_start_method` can be called **once**; libraries should use `mp.get_context("spawn")`.
- **Process lifecycle**: `start()`, `join()`, `is_alive()`, `exitcode` (0 ok, `n` from `sys.exit(n)`, negative = killed by a signal), `terminate()`. Daemon processes die with the parent.
- **Pool**: `map` (list, ordered), `imap` (lazy, ordered), `imap_unordered` (first-finished), `starmap` (args tuples), `apply_async` (+ `callback`/`error_callback`, `get(timeout=)`).
- **`chunksize`** sends many items per message — a huge win for tiny tasks (about 250x in the demo). **`maxtasksperchild`** recycles workers.
- **`ProcessPoolExecutor`**: same Future API as threads; a worker that dies hard gives `BrokenProcessPool` instead of hanging.
- **Picklable**: module-level functions/classes, builtins, `functools.partial` of a module-level function. **Not**: lambdas, nested functions, open files, locks, generators.
- **Data cost**: big arguments are copied each call — send a file name or a range, not the data.
- **`Value` / `Array`**: shared C types; use `get_lock()` for `+=`. **`SharedMemory`**: named raw bytes, zero copy. **`Manager`**: shared dict/list/Namespace through proxies (convenient, slow).
- **Message passing**: `Queue` + one `None` sentinel per worker; `JoinableQueue` with `task_done()`/`join()`; `Pipe` for exactly two endpoints.
- **`initializer`** runs once per worker — seed the RNG, open connections, install a shared lock.
- **Map-reduce**: workers return small `Counter`s, the parent merges with `+`.

## Gotchas (the part worth revising twice)
- **Spawn re-imports the file**: targets must be module-level, and side effects must sit under `if __name__ == "__main__":`. The child's module name is `__mp_main__`, and runtime changes the parent made to globals are **not** visible to the child (under `fork` they would be — code behaves differently per OS).
- **`with Pool() as p:` calls `terminate()`**, not `close()`+`join()`. Collect your results inside the block or running work is killed.
- **Worker exceptions** are re-raised in the parent by `map`/`get()`/`result()`, with the worker's traceback attached as `__cause__` (a `RemoteTraceback`).
- **Locks cannot be passed as `Pool.map` arguments** (`RuntimeError`). Give them to workers through `initializer`, or pass at `Process` creation.
- **`Value` without a lock loses updates**, just like threads. `Manager` nested objects: `d["items"].append(x)` is **lost**; reassign `d["items"] = d["items"] + [x]`.
- **`SharedMemory` cleanup**: every process `close()`s, exactly one owner `unlink()`s; release `memoryview`s *before* `close()` (else `BufferError`). The OS may round the size up.
- Drain a result queue **before** joining the workers; `q.empty()` is unreliable — use `get(timeout=)` and `queue.Empty`.
- Never assert on speedups: small jobs may be slower than serial because of startup and pickling cost. `os.cpu_count()` can exceed what a container really allows (`os.sched_getaffinity(0)`, Linux only).
- `fork` copies the parent's random state: every worker would produce the same "random" numbers unless re-seeded.

## When it matters
CPU-heavy work in pure Python (number crunching, parsing, image/text processing): split into chunks, map across a pool, merge. Use threads or asyncio for waiting on I/O, and always keep the work per task large enough to beat the copy cost.

## One-line recap example
```python
from concurrent.futures import ProcessPoolExecutor

def square(n):                      # must be module-level
    return n * n

if __name__ == "__main__":          # required with spawn
    with ProcessPoolExecutor() as ex:
        print(list(ex.map(square, range(5))))   # [0, 1, 4, 9, 16]
```
