# Threading Primitives — Notes

## What this covers
The full toolbox `threading` gives you beyond a basic `Thread` + `Lock`: how races happen, every synchronization primitive, `concurrent.futures` in depth, deadlocks, and when threads actually help.

## Key points
- **Race condition** = `x += 1` is really three steps (read, add, write). If another thread slips in between, one update is lost. The file proves it with a forced yield point and with a hand-choreographed interleaving.
- **`Lock`** guards shared data — always use `with lock:` so it is released even if the body raises. Keep the locked part tiny.
- **`acquire(blocking=False)` / `acquire(timeout=...)`** return a bool instead of hanging — the way to *detect* trouble.
- **`RLock`** lets the *same* thread acquire again (needed when locked methods call other locked methods). A plain `Lock` re-acquired by its owner waits for itself forever.
- **`Event`** = a flag threads can wait on. Two patterns: *start gate* (everyone waits, then `set()`) and *stop flag* (cooperative shutdown — threads cannot be killed from outside).
- **`Condition`** = lock + waiting room: `wait_for(predicate)` sleeps until something is true; `notify_all()` wakes sleepers. A bounded buffer (producer/consumer) is built from it — that is what `queue.Queue(maxsize)` does.
- **`Semaphore(N)`** = at most N at once. **`BoundedSemaphore`** also raises `ValueError` on an extra `release()`.
- **`Barrier(N)`** = N threads meet; all are released together. **`Timer`** = run a function once, later (`cancel()` before it fires).
- **`threading.local()`** = each thread gets its own private attributes.
- **Daemon threads** are killed abruptly at interpreter exit; non-daemon threads are waited for.
- **`concurrent.futures`**: `as_completed` = finish order, `map` = input order; `wait(return_when=FIRST_COMPLETED / FIRST_EXCEPTION / ALL_COMPLETED)`; `add_done_callback`; `initializer` for per-worker setup; `shutdown(wait=False, cancel_futures=True)` drops the backlog.
- **Deadlock** fixes: one global lock order, or try-acquire and back off. Detect with timeouts.
- **Atomic under the GIL**: single C calls like `list.append`, `dict[k] = v`, `deque.append/popleft`, `Queue` methods. **Not atomic**: `x += 1`, `d[k] += 1`, check-then-act.
- Threads speed up **I/O-bound** work (about 8x in the demo) but not **CPU-bound** pure Python (about 1x) because of the GIL.

## Gotchas (the part worth revising twice)
- **"It never failed in my tests" proves nothing.** Without a forced yield a race may show once in a million runs. Protect shared mutable state anyway.
- **Exceptions in a plain `Thread` are lost** — only that thread dies, a traceback goes to stderr, and `join()` raises nothing. Capture with `threading.excepthook`, or use a `Future` and call `.result()`.
- `Future.cancel()` only works on work that has **not started**: a running future returns `False`. Queued ones can be cancelled.
- A cancelled future's `.result()` raises `CancelledError`; a done-callback on an already-finished future runs **immediately in your thread**, otherwise in the worker thread.
- `time.sleep()` cannot be interrupted; `stop_event.wait(timeout)` returns instantly when the flag is set. Use it for loops that must shut down fast.
- Always re-check the condition after waking (`wait_for`) — never assume one `wait()` means the state you wanted.
- Do not call unknown code (callbacks) while holding a lock — that is how hidden deadlocks appear. Livelock (everyone keeps backing off) needs random jitter; starvation needs fairness.
- `t.run()` runs in the *caller's* thread — call `t.start()`. `daemon` must be set before `start()`.
- The GIL is an implementation detail. In free-threaded builds (3.13+, experimental) bad locking breaks sooner — explicit locks keep you correct on both.

## When it matters
Any time threads share data (counters, caches, result lists), run network/disk waits in parallel (downloaders, API fan-out), or must shut down cleanly (servers, workers). For CPU-heavy pure-Python work use processes instead (see `12-Multiprocessing-Pool-And-Shared-State`).

## One-line recap example
```python
import threading
lock, total = threading.Lock(), 0

def add():
    global total
    with lock:          # read-modify-write is now one safe unit
        total += 1

ts = [threading.Thread(target=add) for _ in range(100)]
[t.start() for t in ts]; [t.join() for t in ts]
print(total)  # 100
```
