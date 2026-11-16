# Async HTTP and Concurrency — Notes

## What this covers
`asyncio` with `httpx.AsyncClient` and `aiohttp` against a local stdlib server on `127.0.0.1` port 0: `gather`, `TaskGroup`, `Semaphore` rate limiting, `asyncio.timeout`, retries, cancellation, async context managers, `to_thread` / `ThreadPoolExecutor` for blocking calls, and an `asyncio.Queue` producer/consumer. Sequential vs concurrent is compared by call counts, ordering and the server's "max in flight" counter — never by timing.

## Key points
- Async gives concurrency on one thread for I/O-bound work; it does nothing for CPU-bound work.
- `async def` returns a coroutine that does nothing until awaited or wrapped in a Task. Call `asyncio.run(main())` once at the top.
- `gather` returns results in input order; `return_exceptions=True` keeps one failure from hiding the rest.
- `TaskGroup` (3.11+) cancels siblings on failure and raises an `ExceptionGroup` (catch with `except*`).
- `Semaphore(N)` caps in-flight work; a bounded `Queue` plus N workers does the same and adds back-pressure.
- `async with asyncio.timeout(s)` is a total deadline over many awaits; clients also have their own per-request timeouts.
- Retries: back off with `await asyncio.sleep`, retry only transient errors and idempotent requests.
- Reuse one `AsyncClient` / `ClientSession`; always open it with `async with`.
- Wrap blocking code with `asyncio.to_thread` (or `run_in_executor`); `pool.map` keeps input order.

## Gotchas (the part worth revising twice)
- `time.sleep`, `requests`, or a CPU loop inside a coroutine freezes the whole loop.
- Forgetting `await` gives a coroutine object, not a result.
- `create_task` keeps only a weak reference — store tasks in a set, or use `TaskGroup`.
- `CancelledError` is a `BaseException`; if you catch it, re-raise it, or timeouts and TaskGroups break.
- With plain `gather`, one failure raises immediately but the other tasks keep running.
- `as_completed` yields in completion order, so tag results with an id.
- `asyncio.run()` fails inside an already running loop.
- aiohttp does not raise on 4xx/5xx unless `raise_for_status=True`; a new session per request loses connection reuse.
- Create `Semaphore`/`Queue`/`Lock` inside the running loop, not at import time.
- Shut down helper servers in order: `shutdown()`, `server_close()`, `join()`; use daemon threads so a sleeping handler cannot delay exit.

## When it matters
Calling many APIs, crawling, fan-out/fan-in pipelines, and services that wait on I/O far more than they compute.

## One-line recap example
```python
import asyncio
async def work(n):
    await asyncio.sleep(0.01)
    return n * 2
async def main():
    return await asyncio.gather(*(work(n) for n in range(3)))
print(asyncio.run(main()))   # [0, 2, 4]
```
