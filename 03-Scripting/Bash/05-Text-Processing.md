# Bash Text Processing — Notes

## What this covers
The core Unix text-processing toolkit: pipes, redirection, `grep`, `sed`, `awk`, `cut`, `sort`/`uniq`, and chaining them into a real pipeline.

## Key points
- `|` feeds one command's stdout into the next command's stdin.
- Redirection: `>` overwrites a file, `>>` appends, `<` feeds a file as stdin, `2>&1` sends stderr to wherever stdout is going, `2>/dev/null` discards stderr.
- `grep pattern file`: `-i` case-insensitive, `-v` invert match, `-c` count matches.
- `sed 's/old/new/' file` replaces the first match per line; add `g` (`s/old/new/g`) for all matches per line.
- `awk -F',' '{ print $2 }' file`: splits each line into fields on the `-F` delimiter (default whitespace); `$0` is the whole line; `NR > 1` skips a header row.
- `cut -d',' -f1,3 file` extracts whole fields by delimiter; `cut -c1-8` extracts a fixed character range — lighter-weight than awk for simple extraction.
- `sort` orders lines; `uniq` only collapses **adjacent** duplicates (so input to `uniq` should almost always be sorted first); `uniq -c` prefixes each line with its count.

## Gotchas (the part worth revising twice)
- `uniq` without a preceding `sort` silently misses non-adjacent duplicates — it's not a general dedup tool.
- A common "top value" pipeline is `awk (extract column) | sort | uniq -c | sort -nr | head -1` — order matters: sort before uniq -c, then sort -nr (numeric reverse) to rank the counts.
- `2>&1` placement matters: it must come after the stdout redirect (`cmd > file 2>&1`) to actually merge stderr into the same file; reversed order sends stderr to the terminal instead.

## When it matters
Any time you're parsing logs, CSVs, or command output in a script instead of reaching for a heavier scripting language — this pipeline style is the bash-native way to do that.

## One-line recap example
```bash
awk -F',' 'NR > 1 { print $3 }' data.csv | sort | uniq -c | sort -nr | head -1
# most frequent value in column 3
```
