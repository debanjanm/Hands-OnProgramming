# Regular Expressions — Notes

## What this covers
Using the `re` module to search, match, extract, and replace text with patterns — from basic matching through groups, lookaheads, and performance pitfalls.

## Key points
- `re.match(pattern, s)` matches only at the **start** of the string; `re.search(pattern, s)` finds a match **anywhere**.
- `re.findall(pattern, s)` returns all non-overlapping matches as a list; `re.finditer()` gives an iterator of match objects (with `.group()` and `.span()` for position).
- `re.sub(pattern, replacement, s)` finds and replaces; `re.split(pattern, s)` splits a string on a pattern.
- Common building blocks: `\d` digit, `\w` word char, `\s` whitespace, `.` any char, `+` one-or-more, `*` zero-or-more, `?` optional, `{n,m}` range, `^`/`$` start/end of string.
- Groups: `(...)` captures part of a match, accessed via `match.group(1)`, `.group(2)`, etc. Named groups `(?P<name>...)` are accessed via `match.groupdict()` or `.group("name")`.
- `re.compile(pattern)` precompiles a pattern for efficient reuse when matching many strings against the same pattern.
- Lookaheads/lookbehinds check for a pattern **without** including it in the match: `(?=...)` positive lookahead, `(?!...)` negative lookahead, `(?<=...)` positive lookbehind, `(?<!...)` negative lookbehind.
- Backreferences (`\1`, `\2`, ...) match text a prior group already captured — useful for catching repeated words. Named version: `(?P=name)`.
- `re.VERBOSE` (`re.X`) lets you spread a pattern across multiple lines with comments and ignored whitespace, for readability.

## Gotchas (the part worth revising twice)
- **Greedy vs non-greedy**: quantifiers (`*`, `+`, `?`, `{n,m}`) are greedy by default — they match as much as possible (`<.*>` on `<b>x</b>` spans to the LAST `>`). Add `?` after them (`<.*?>`) to make them non-greedy/lazy — matches as little as possible, stopping at the first `>`.
- **Catastrophic backtracking**: nested quantifiers like `(a+)+` can force the regex engine to try an exponential number of ways to split the input before giving up on a failed match — a pattern like `(a+)+b` against a long run of `a`s with no trailing `b` can hang a program for minutes. Avoid nested/ambiguous quantifiers; prefer a flatter equivalent like `a+b`.
- Forgetting `encoding`/raw strings (`r"..."`) is a common source of bugs — always use raw strings for regex patterns so backslashes aren't interpreted by Python first.

## When it matters
Validation (emails, formats), extracting structured data from unstructured text, and search/replace across text — but reach for a real parser instead of regex once the structure gets nested or complex (e.g. don't parse HTML/JSON with regex).

## One-line recap example
```python
import re
re.findall(r"\d+", "I have 3 cats and 12 fish")   # ['3', '12']
```
