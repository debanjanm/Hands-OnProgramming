# Subprocess And Signals — Notes

## What this covers
How your Python script starts other programs (`subprocess`), how the operating system pokes your script (`signal`), and how to exit cleanly (`atexit`, exit codes). `03-Os-And-Sys.py` only shows a taste; this goes deep.

## Key points
- **`subprocess.run(list_args, capture_output=True, text=True, timeout=N, check=True)`** is the default recipe: start, wait, collect. It returns a `CompletedProcess` with `.args`, `.returncode`, `.stdout`, `.stderr`.
- **`run()` does NOT raise on failure by default.** `check=True` turns a non-zero exit into `CalledProcessError`; `timeout=` turns a hang into `TimeoutExpired` (and kills the child for you).
- **Other `run()` options**: `input=` feeds stdin, `cwd=` sets the child's folder, `env=` sets its environment variables (copy ours first: `{**os.environ, "X": "1"}`).
- **Run Python in a child** with `[sys.executable, "-c", "code"]` or `[sys.executable, "-m", "module"]`. Never the bare string `"python"`.
- **`Popen`** = start without waiting. Use it for pipes (`stdout=PIPE`, feed one process's stdout to the next one's `stdin`), streaming (`for line in proc.stdout`), and stopping a child (`terminate()` then `kill()`).
- **`communicate()`** reads stdout and stderr together and then waits. It is the safe way to collect output.
- **`stderr=subprocess.STDOUT`** merges errors into the normal output stream.
- **Return codes**: `0` = success, positive = the program's own error code, **negative (`-15`, `-9`) = killed by that signal** (POSIX).
- **`shlex`**: `split` (string to safe list), `quote` (make one piece shell-safe), `join` (list to string).
- **Signals**: `SIGINT` (Ctrl+C, becomes `KeyboardInterrupt`), `SIGTERM` (polite stop), `SIGKILL` (cannot be caught), `SIGALRM` (timer). `signal.Signals` is the enum of them all.
- **`signal.signal(sig, handler)`** installs `handler(signum, frame)`. Keep it tiny: set a flag, let the main loop do the real work.
- **`atexit.register(fn)`** runs cleanup at exit, **last registered runs first**.
- **Exit codes**: `main()` returns a code, only the bottom of the file calls `sys.exit(main())`. Convention: `0` ok, `1` runtime error, `2` bad usage, `130` Ctrl+C.

## Gotchas (the part worth revising twice)
- **Shell injection**: `subprocess.run(f"echo {user_text}", shell=True)` lets `; other-command` in the text run a second command. Use list args (no shell). If you must use a shell, wrap untrusted pieces in `shlex.quote()`.
- **Forgetting the return code** means failures pass silently. Use `check=True` or look at `returncode`.
- **Pipe deadlock**: a pipe buffer is small. If you `proc.wait()` while the child is blocked writing to a full pipe, both sides wait forever. Use `communicate()` (or `run(capture_output=True)`), or send output to a file.
- **No timeout = a hung child hangs you forever.**
- **`env={...}` replaces the entire environment** (no `PATH`, no `HOME`). Copy `os.environ` and add to it.
- **A missing program** raises `FileNotFoundError` before any process exists, so there is no return code to check.
- **A piped child buffers its stdout**, so output can look out of order against stderr. Use `flush=True` (or `python -u`) in the child; it also matters for live streaming.
- **`os.system`** always uses a shell, cannot capture output or time out. Don't use it.
- **Handlers run only in the main thread**; `signal.signal()` from another thread raises `ValueError`. Workers should watch a `threading.Event`.
- **A handled `SIGTERM` gives exit code 0, not -15**; an unhandled one gives -15 and skips `atexit`.
- **`atexit` does not run** after `os._exit()`, `SIGKILL`, or a default `SIGTERM`. Make your `SIGTERM` handler call `sys.exit()` if you want cleanup.
- **`signal.alarm` and `SIGALRM`** are POSIX only, whole seconds only, main thread only. Always cancel and restore the old handler.

## When it matters
Automation scripts calling `git`, `ffmpeg`, `docker`, `pip`; CI/deploy tools that depend on exit codes; services that must shut down gracefully on `SIGTERM` (Docker, Kubernetes); any "run this flaky command with retries" helper (`timeout` per attempt + exponential backoff + don't retry permanent errors).

## One-line recap example
```python
import subprocess, sys
r = subprocess.run([sys.executable, "-c", "print('hi')"], capture_output=True, text=True, timeout=10, check=True)
print(r.stdout.strip(), r.returncode)   # hi 0
```
