# Text Utilities — Notes

## What this covers
The small standard-library tools for text jobs people often hand-roll: `textwrap`, `string`, `difflib`, `pprint`, `reprlib`, `unicodedata`, `shlex`, `fnmatch`, `html`, `locale` — plus a word-count / slugify / report example.

## Key points
- **`textwrap`**: `wrap()` → list of lines, `fill()` → one string, `shorten()` → cut with `[...]`, `dedent()` → remove common indent (use on `"""` blocks), `indent()` → add a prefix to each line. `TextWrapper` stores options (`initial_indent`, `subsequent_indent`, `max_lines`, `break_long_words`).
- **`string`**: constants (`ascii_letters`, `digits`, `punctuation`, `hexdigits`), `capwords()`, and **`Template`** (`$name` placeholders). `substitute()` is strict (`KeyError` if missing); `safe_substitute()` leaves unknown names alone.
- **`string.Formatter`**: the engine behind `str.format` — subclass it to customise lookups; `parse()` shows how a format string is split.
- **`difflib`**: `SequenceMatcher(None, a, b).ratio()` (0 to 1 similarity), `get_close_matches()` for "did you mean?", `unified_diff()` (git-style), `ndiff()` (with `?` hints), `HtmlDiff` (side-by-side HTML page).
- **`pprint`**: `pprint()` prints, `pformat()` returns a string. Options: `width`, `depth`, `sort_dicts=False`, `compact`, `PrettyPrinter(indent=...)`.
- **`reprlib.repr()`**: short repr of huge containers (`[0, 1, 2, 3, 4, 5, ...]`). `@recursive_repr` protects `__repr__` of self-referencing objects.
- **`unicodedata`**: `normalize("NFC"/"NFD"/"NFKC")`, `category()`, `name()`, `east_asian_width()`, `combining()`.
- **`shlex`**: `split()` (shell-style quoting), `quote()` (make a string safe for a shell), `join()`.
- **`fnmatch`**: `fnmatch`, `fnmatchcase`, `filter`, `translate` — wildcard matching on strings (`*`, `?`, `[abc]`, `[!abc]`), no disk access.
- **`html.escape` / `html.unescape`**: make `< > & " '` safe for HTML and reverse it.
- **`locale`**: regional number formats; `format(n, ",.2f")` gives thousands separators without it.
- **Regex** lives in `05-Python Advanced/07-Regular-Expressions.py`.

## Gotchas (the part worth revising twice)
- **The same-looking "é" can be two different strings**: one code point (`é`) or `e` + combining accent (`é`). They look equal, but `==` is `False`, `len` differs (4 vs 5) and dict lookups miss. Normalise both sides with `unicodedata.normalize("NFC", s)` first.
- **Use `casefold()`, not `lower()`, for case-insensitive compare**: `"Straße".casefold() == "STRASSE".casefold()` is `True`; with `lower()` it is `False`.
- **Strip accents** = NFD, then drop characters of category `Mn`. Letters like `ß` and `ø` have no decomposition and stay as they are.
- **`str.isdigit()` accepts other scripts' digits** (Arabic-Indic `٣` → `True`, `int()` works too). For "0–9 only" use `string.digits` or `re.ASCII`.
- **`len()` is not display width**: CJK characters take 2 columns (`east_asian_width` `W`/`F`). Alignment code needs a width function.
- **`str.format` with a template written by a user can leak data** (`{a._api_key}` printed the secret). Use `string.Template` when the template text is untrusted.
- **`str.title()` capitalises after apostrophes** (`They'Re`); `string.capwords()` does not.
- **`textwrap.fill()` merges paragraphs** (newlines count as whitespace) — split on blank lines and wrap each one. A long word with no spaces (a URL) is chopped unless `break_long_words=False`.
- **`difflib` ratio is character-based, case-sensitive, and can differ with argument order** — lowercase first, and treat it as "roughly similar", not "means the same".
- **`fnmatch.fnmatch` follows OS case rules** (insensitive on Windows); use `fnmatchcase` for portable behaviour. Its `*` also matches `/` and leading dots, unlike real `glob`.
- **`locale.setlocale` is process-wide and the locale must be installed** — wrap in `try/except locale.Error` and restore it afterwards.
- **`html.escape` twice gives `&amp;lt;`** — escape once, at output time. Escaping is for HTML only, not SQL or shell.
- `shlex.quote` + a shell is a fallback; passing a **list** of arguments to `subprocess` (no shell) is safer.

## When it matters
Command-line tools (wrapping help text, "did you mean" hints, parsing quoted arguments), reports and logs (`pprint`, `reprlib`), anything that compares or searches user text (names with accents, mixed case, copy-pasted Unicode), generating HTML or URL slugs, and showing diffs of config or text.

## One-line recap example
```python
import unicodedata
a, b = "café", "café"                      # both display as "café"
norm = lambda s: unicodedata.normalize("NFC", s).casefold()
print(a == b, norm(a) == norm(b))                     # False True
```
