# Bash Process And Job Control — Notes

## What this covers
Process IDs, running commands in the background, waiting on them, signal handling with `trap`, and killing your own processes.

## Key points
- `$$` is the current script's own process ID — handy for unique temp filenames and identifying "my own" process.
- `command &` runs it in the background; the shell moves on immediately without waiting. `$!` holds the PID of the most recently backgrounded process. `jobs` lists background jobs started by the current shell session.
- `wait PID` blocks until that process finishes (and returns its exit code); bare `wait` blocks until all background jobs finish.
- `trap 'commands' SIGNAL` runs `commands` when that signal arrives. `EXIT` is a pseudo-signal that fires on any script exit — the standard place for cleanup. `INT` is Ctrl-C.
- `kill PID` sends SIGTERM (a graceful stop request) by default. Only kill processes you actually started/control.
- `ps -p PID -o pid,ppid,comm` shows info for one specific process.

## Gotchas (the part worth revising twice)
- A backgrounded job **inherits its parent shell's traps**, including an `EXIT` trap. If the parent has `trap cleanup EXIT` and you background a subshell that gets killed, the inherited trap fires *inside the child* too — confusing and unintended. Clear it explicitly in the child: `( trap - EXIT; exec sleep 100 ) &`.
- After `kill`-ing a background job, `wait PID` on it to reap it and silence the shell's "Terminated" job-control notice.
- `kill -0 PID` doesn't actually send a signal — it just checks whether the process still exists (exit code 0 = alive), useful for confirming a kill actually worked.

## When it matters
Any script that launches background work (parallel tasks, long-running servers) needs `wait` to synchronize and a trap-based cleanup — and needs to remember trap inheritance so cleanup doesn't fire in the wrong place.

## One-line recap example
```bash
( trap - EXIT; exec sleep 100 ) &   # clear inherited EXIT trap before backgrounding
long_pid=$!
kill "$long_pid"; wait "$long_pid" 2>/dev/null   # kill, then reap
```
