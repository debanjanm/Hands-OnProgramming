# Bash Functions And Arguments — Notes

## What this covers
Defining and calling functions, positional parameters, the `"$@"` vs `"$*"` distinction, how return values actually work, `local` scoping, and default argument values.

## Key points
- Define with `name() { ...; }` or `function name { ...; }`. Call with just `myfunc a b c` — no parentheses at the call site.
- Inside a function: `$1 $2 ...` are the arguments, `$#` is the count, `$@`/`$*` mean "all arguments".
- `return N` sets the function's **exit code** (0-255), read via `$?` — it signals success/failure, it does not carry data.
- To return actual data, `echo` it and capture with `result=$(myfunc args)`.
- `local varname=value` scopes a variable to the function. Without `local`, an assignment inside a function is global and silently clobbers/creates a variable of the same name outside.
- `${1:-default}` expands to `default` if the argument is unset or empty, without changing the variable — handy for optional args.

## Gotchas (the part worth revising twice)
- `"$@"` expands to each argument as its own separate quoted word (preserves spaces inside args). `"$*"` joins ALL arguments into one single word. Unquoted, both behave the same (everything word-splits). Almost always want `"$@"`.
- Forgetting `local` is a silent bug — the function looks self-contained but leaks into and overwrites global state. `leaky_function` in this file sets `counter=1` with no `local` and clobbers the caller's `counter`.
- `return` is not `echo`: `return 5` gives you exit code 5 via `$?`, it does not make `$(myfunc)` print `5`.

## When it matters
Any script split into reusable functions — the `"$@"` vs `"$*"` and `local` gotchas are exactly what breaks a "working" function the moment it's called with multi-word arguments or reused elsewhere in a bigger script.

## One-line recap example
```bash
add() { echo $(( $1 + $2 )); }   # "return" data via echo + capture
result=$(add 3 5)
echo "$result"   # 8
```
