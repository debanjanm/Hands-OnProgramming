# Advanced Bash — Notes

## What this covers
Process substitution, heredocs/herestrings, the full meaning of `set -euo pipefail`, subshells vs command groups, and passing arrays into functions.

## Key points
- Process substitution `<(command)` exposes a command's output as a file path (via a FIFO) — lets tools that expect a filename (like `diff`) consume command output directly, no temp file needed.
- Heredoc `<<EOF ... EOF` feeds multi-line text as stdin; `<<'EOF'` (quoted marker) disables variable expansion inside, unquoted allows it. Herestring `<<<"string"` is a one-line shorthand for piping a variable into stdin.
- `set -e` (errexit): exit immediately on any nonzero exit code — *except* inside an `if`/`while` condition, an `&&`/`||` chain, or a negated (`!`) command.
- `set -u` (nounset): referencing an unset variable is an error instead of silently becoming an empty string — catches typos.
- `set -o pipefail`: makes a whole pipeline fail if *any* stage fails, not just the last one (normally only the last command's exit code counts).
- Subshell `( commands )` runs in a separate child process — variable changes inside do NOT leak out. Command group `{ commands; }` runs in the same shell — changes DO persist. (Note: `{ }` requires spaces and a trailing `;` before the closing brace.)
- Pass an array into a function by expanding it: `myfunc "${arr[@]}"`; rebuild it inside with `local -a received=("$@")`.

## Gotchas (the part worth revising twice)
- **`-e` is suppressed while bash evaluates the condition of an `if`/`while`/`&&`/`||`** — and that suppression is inherited even by a subshell started there, even if the subshell runs its own `set -e`. A subshell must run as its own standalone statement (not on the left of `||`) for `-e` to actually take effect inside it; check its result afterward via `$?` instead.
- This curriculum deliberately omits `-e` at the top-level of every lesson script, because several lessons intentionally run commands that are supposed to fail (to demonstrate exit codes), and `-e` would kill the whole script instead of letting `|| true`/`if` handle it.
- `pipefail` matters exactly when a non-last stage fails: `false | true` looks like success (exit 0) without pipefail, and correctly fails with it.

## When it matters
`set -euo pipefail` is close to a default for any real-world bash script — but the subshell/condition-suppression gotcha is why "it has `set -e` so it's safe" isn't always true; test the actual failure paths.

## One-line recap example
```bash
(
    set -e
    false        # aborts the subshell here, standalone statement (not on the left of || or &&)
)
echo "subshell exit code: $?"   # nonzero -> -e worked
```
