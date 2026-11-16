# Bash Fundamentals — Notes

## What this covers
The absolute basics of a bash script: the shebang, variables, quoting, command substitution, constants, and exit codes.

## Key points
- **Shebang** `#!/usr/bin/env bash` picks up `bash` from PATH (portable) instead of hardcoding `/bin/bash`. Only matters when you run the file directly (`./script.sh`); `bash script.sh` ignores it.
- **Assignment**: no spaces around `=`. `x = 5` is not assignment, it's a command call and fails.
- Variables are untyped strings by default, even numbers. Expand with `$x` or `${x}` (braces needed to disambiguate, e.g. `${name}Script`).
- **Quoting**: no quotes = word-splitting + glob expansion happens. Double quotes = expansion happens but result stays one word. Single quotes = nothing expands, fully literal.
- **Command substitution**: `$(command)` captures a command's stdout. Prefer it over backticks (legacy, doesn't nest cleanly).
- `readonly NAME=value` makes a constant; reassigning it is an error.
- Every command has an exit code (`$?`): `0` = success, `1-255` = failure. `$?` only holds the *most recent* command's code — check it immediately.
- `#` starts a comment to end of line; no multi-line comment syntax exists.

## Gotchas (the part worth revising twice)
- Unquoted variables are the #1 source of bash bugs: they get word-split on whitespace and glob-expanded. `value="hello   world"` unquoted collapses the spacing; a variable holding `*.txt` unquoted actually expands as a glob.
- `$?` is overwritten by the very next command — capture it into a variable if you need it later.
- Backticks vs `$(...)`: backticks need escaping to nest, `$(...)` nests trivially. Always prefer `$(...)`.

## When it matters
Every bash script starts here — quoting discipline in particular is the thing that silently breaks scripts the moment a filename has a space in it.

## One-line recap example
```bash
name="Bash Script"
echo "$name"      # safe: one word, spaces preserved
echo $name        # risky: word-splits into two words
```
