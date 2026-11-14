# Async/Await — Notes

## What this covers
`asyncio`-based concurrency: coroutines that cooperatively pause and resume with `await`, letting one thread handle many I/O-bound tasks at once.

## Key points
- `async def` defines a coroutine function. `await` pauses it until the awaited operation completes, letting other coroutines run in the meantime. `asyncio.run(coro())` runs a top-level coroutine.
- Calling `await task_a(); await task_b()` one after another runs them **sequentially** — no concurrency gain, total time adds up.
- `asyncio.gather(task_a(), task_b())` runs coroutines **concurrently** — total time is closer to the slowest one, not the sum.
- `asyncio.create_task(coro())` schedules a coroutine to start running immediately in the background, without waiting — "fire it now, await the result later".
- `asyncio.wait_for(coro(), timeout=N)` raises `asyncio.TimeoutError` if the coroutine doesn't finish in time.
- Async generators (`async def` with `yield`) are consumed with `async for`.
- Async context managers implement `__aenter__`/`__aexit__` (both coroutines) and are used via `async with` — same idea as sync context managers, but setup/teardown can itself await other async work.
- `asyncio.Queue` is the async equivalent of `queue.Queue` for producer/consumer coroutines that hand off work without blocking the event loop.
- `asyncio.Lock` protects shared state between coroutines — used via `async with lock:`.
- `task.cancel()` raises `asyncio.CancelledError` inside the target coroutine at its current `await` point.
- `loop.run_in_executor(None, blocking_fn, *args)` runs blocking/CPU-bound/legacy sync code in a thread pool so it doesn't freeze the whole event loop.

## Gotchas (the part worth revising twice)
- Even though asyncio is single-threaded, an `await` **inside** a critical section can let another coroutine interleave and corrupt shared state — asyncio isn't automatically safe just because there's no real parallel execution. Use `asyncio.Lock` around read-modify-write sequences that contain an `await`.
- A cancelled coroutine should generally **re-raise** `asyncio.CancelledError` after any cleanup in its `except` block, not swallow it silently — swallowing it breaks the caller's ability to see that cancellation happened.
- Calling a real blocking function (e.g. `time.sleep()`, not `asyncio.sleep()`) directly inside a coroutine freezes the **entire** event loop, not just that one coroutine — route it through `run_in_executor` instead.
- Choosing between asyncio / threading / multiprocessing: asyncio for many I/O-bound tasks with no shared-state race conditions (single-threaded); threading for I/O-bound work with a simpler mental model (but GIL-limited); multiprocessing for CPU-bound work needing true parallelism.

## When it matters
Reach for asyncio when you have many concurrent I/O-bound operations (API calls, DB queries, sockets) and want high concurrency without the overhead of one OS thread per task.

## One-line recap example
```python
import asyncio

async def main():
    results = await asyncio.gather(asyncio.sleep(1, result="A"), asyncio.sleep(1, result="B"))
    print(results)   # ['A', 'B'] after ~1s total, not 2s
```
