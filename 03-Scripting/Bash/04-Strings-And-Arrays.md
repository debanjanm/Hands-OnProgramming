# Bash Strings And Arrays — Notes

## What this covers
String operations (length, substring, replace, case conversion) and both indexed and associative arrays.

## Key points
- Length: `${#var}`. Substring: `${var:offset:length}` (offset is 0-based, omit length for "rest of string").
- Replace: `${var/old/new}` replaces the first match, `${var//old/new}` replaces all. `${var/#old/new}` anchors to start, `${var/%old/new}` to end.
- Case conversion (bash 4+): `${var^^}` uppercase, `${var,,}` lowercase, `${var^}`/`${var,}` convert only the first character.
- Indexed arrays: `arr=(a b c)`, 0-indexed. `"${arr[@]}"` expands each element as a separate word (like `"$@"`), `${#arr[@]}` is the count, `arr+=(x)` appends.
- Associative arrays: `declare -A name` then `name[key]=value`, keys are arbitrary strings. `${!name[@]}` lists keys.

## Gotchas (the part worth revising twice)
- Negative substring offset needs a space before the `-`: `${text: -5}` not `${text:-5}` — the latter is parsed as the "default value" operator (`${var:-default}`), a completely different thing.
- **macOS ships bash 3.2** (Apple never upgraded past the last GPLv2 release — a licensing choice, not an oversight). `${var^^}`, `${var,,}`, and `declare -A` all need bash 4+ and simply don't exist on stock macOS bash. Check with `((BASH_VERSINFO[0] >= 4))` and fall back to `tr '[:lower:]' '[:upper:]'` for case conversion, or parallel indexed arrays (keys array + values array, matched by index) instead of `declare -A`.
- Always quote `"${arr[@]}"` when looping — unquoted, elements containing spaces get re-split into multiple words.

## When it matters
Any script that needs to run on both Linux (bash 4/5) and stock macOS — write the version check and fallback up front rather than discovering `declare -A: command not found` on a teammate's Mac.

## One-line recap example
```bash
if ((BASH_VERSINFO[0] >= 4)); then
    echo "${mixed^^}"                              # bash 4+
else
    echo "$mixed" | tr '[:lower:]' '[:upper:]'      # portable fallback (macOS bash 3.2)
fi
```
