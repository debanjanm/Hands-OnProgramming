# Bash Control Flow — Notes

## What this covers
Conditionals (`[ ]` vs `[[ ]]`), comparisons, `case`, and the loop forms (`for`, C-style `for`, `while`, `until`, `break`/`continue`).

## Key points
- `[ ]` is literally the `test` command — spaces around the brackets are mandatory (they're argument separators, not decoration).
- `[[ ]]` is a bash keyword, parsed specially: unquoted variables inside it are safe (no word-splitting/glob expansion), and it supports `&&`, `||`, glob matching (`==`), and regex (`=~`) directly.
- Numeric comparison: `-eq -ne -gt -ge -lt -le`. String comparison: `= ==` (equal), `!=`, `< >` (lexical, needs `[[ ]]` since `< >` mean redirection in `[ ]`).
- `case "$val" in pattern) ... ;; esac` matches against glob patterns; `;;` stops, `;;&` (bash 4+) keeps testing later patterns.
- Loop forms: `for x in list; do ... done`, C-style `for (( i=0; i<3; i++ ))`, `while cond; do ... done` (runs while true), `until cond; do ... done` (runs while false).
- `break` exits a loop entirely; `continue` skips to the next iteration.

## Gotchas (the part worth revising twice)
- `[ "$var" = foo ]` with an empty/unset `$var` unquoted becomes `[ = foo ]` — "unary operator expected" error. Always quote inside `[ ]`. `[[ ]]` doesn't have this problem even unquoted.
- `-eq` vs `==`: `[ 5 -eq 05 ]` is true (numeric), but `[[ "5" == "05" ]]` is false (string compare — different characters).
- When looping over globbed files (`for f in "$dir"/*.txt`), quote the loop variable inside the body too — protects filenames with spaces from re-splitting.

## When it matters
Any script that branches on input, validates arguments, or processes a list of files needs this — and the `[ ]` vs `[[ ]]` quoting gotcha is exactly where scripts break on real-world (space-containing) filenames.

## One-line recap example
```bash
name=""
[[ -z "$name" ]] && echo "empty, and this is safe even unquoted"
[ -z "$name" ] && echo "also fine here, but quote inside [ ] as a habit"
```
