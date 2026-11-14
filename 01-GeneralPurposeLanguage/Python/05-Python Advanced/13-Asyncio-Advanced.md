# Asyncio Advanced — Notes

## What this covers
Doing asyncio well, beyond the basics in `10-Async-Await`: structured concurrency, timeouts, bounded concurrency, cancellation, the classic mistakes, streams, subprocesses, debugging, testing, and a crawler example.

## Key points
- **Mental model**: one thread, one event loop, cooperative scheduling. `await` is the only yield point; code between awaits is never interrupted.
- **`TaskGroup`** (3.11+): tasks live inside a scope. If one fails, siblings are cancelled and you get an **`ExceptionGroup`**, handled with `except*` (matches by type).
- **Timeouts**: `async with asyncio.timeout(s)` covers a whole block (can `reschedule`); `wait_for(x, s)` wraps one awaitable. Both **cancel** the slow work and raise `TimeoutError`.
- **Collecting results**: `gather` = input order; `gather(return_exceptions=True)` returns errors as values; `as_completed` = finish order; `wait(FIRST_COMPLETED / ALL_COMPLETED)` returns `(done, pending)` sets of tasks.
- **`asyncio.Semaphore(N)`** caps in-flight work; `Event` = gate; `Condition.wait_for(predicate)` = wait for a state.
- **Cancellation** raises `CancelledError` at the current `await`. Clean up in `finally`, then **re-raise**. `CancelledError` is not an `Exception` subclass. `shield()` protects inner work from the outer awaiter being cancelled.
- **Blocking code**: `asyncio.to_thread(fn, ...)` (copies contextvars) or `loop.run_in_executor(executor, fn, ...)` for your own pool or a process pool.
- **Async iteration**: `async for`, async generators, `async with`, `@asynccontextmanager`, async comprehensions; use `contextlib.aclosing` for generators you may abandon early.
- **Backpressure**: `asyncio.Queue(maxsize=N)` makes producers wait when full. `task_done()` + `await q.join()`, then cancel the consumers.
- **`contextvars.ContextVar`** is per task; `threading.local` is per thread, so all tasks share it.
- **Streams**: `start_server` / `open_connection` on `127.0.0.1`, port `0` for a free port; `write()` then `await drain()`; always close writer and server.
- **Subprocess**: `create_subprocess_exec` + `communicate()`.
- **Debug mode** (`asyncio.run(..., debug=True)`) logs slow callbacks and where un-awaited coroutines came from. `asyncio.Runner` (3.11+) reuses one loop. Tests: `unittest.IsolatedAsyncioTestCase`. Related: uvloop, trio, anyio.

## Gotchas (the part worth revising twice)
- **Forgot `await`** → you hold a coroutine object, nothing runs, and a "coroutine ... was never awaited" `RuntimeWarning` appears.
- **Blocking the loop** (`time.sleep`, CPU loops, sync I/O) freezes every task — the heartbeat demo stalls. Use `await asyncio.sleep`, `to_thread`, or a process pool.
- **Fire-and-forget `create_task` without keeping a reference**: the loop holds tasks weakly, so they can be garbage collected mid-flight ("Task was destroyed but it is pending!"). Keep them in a set and discard on done.
- **`await` in a loop is sequential** (about 5x slower in the demo); use `gather` or a `TaskGroup`.
- **`gather` (default) does not cancel the other tasks** when one fails — they keep running unattended. `TaskGroup` does cancel them.
- **Swallowing `CancelledError`** makes the task finish "normally" and breaks timeouts and TaskGroups. Cancel a task only after it has started (`await asyncio.sleep(0)` first), otherwise your `try` is never entered.
- Threads started by `to_thread` cannot be cancelled; only the waiting is abandoned.
- Breaking out of `async for` leaves an async generator un-finalised until later; use `aclosing`.
- `except*` is 3.11+ syntax and won't even compile on older Pythons; `asyncio.wait` needs tasks, not bare coroutines.

## When it matters
Many concurrent network waits (crawlers, API fan-out, servers, chat), where you also need limits, timeouts, retries with backoff and a clean shutdown. For a few blocking calls use threads; for CPU work use processes.

## One-line recap example
```python
import asyncio

async def fetch(i):
    await asyncio.sleep(0.01)
    return i

async def main():
    async with asyncio.TaskGroup() as tg:          # 3.11+
        tasks = [tg.create_task(fetch(i)) for i in range(3)]
    print([t.result() for t in tasks])             # [0, 1, 2]

asyncio.run(main())
```
