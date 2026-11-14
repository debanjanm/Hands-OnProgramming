# Json And Csv — Notes

## What this covers
Reading and writing the two most common data-interchange formats: JSON (`json` module — APIs, config) and CSV (`csv` module — tabular data).

## Key points
- **`json.dumps(obj, indent=2)`** — Python object → JSON string. **`json.loads(s)`** — JSON string → Python object.
- **`json.dump(obj, file)`** / **`json.load(file)`** — same, but read/write directly to a file object.
- **`csv.writer(file)`** / **`csv.reader(file)`** — write/read rows as plain lists. Always open with `newline=""` when writing.
- **`csv.DictWriter`** / **`csv.DictReader`** — treat each row as a dict keyed by column headers (`fieldnames=`, `.writeheader()`).
- **Custom JSON encoding** — `json.dumps()` can't serialize `datetime` or custom classes by default. Fix with `default=a_function` (converts unknown types) or a `json.JSONEncoder` subclass overriding `.default()`.
- **`sort_keys=True`** — deterministic key order. **`separators=(",", ":")`** — compact output with no extra spaces.
- **CSV dialects** — `csv.register_dialect(name, delimiter=..., quotechar=...)` for non-comma formats (e.g. pipe-delimited).
- **`csv.Sniffer()`** — auto-detects a CSV's delimiter/dialect and whether it has a header row, from a sample of the text.

## Gotchas (the part worth revising twice)
- `json.dumps()` raises `TypeError` on anything it doesn't know how to serialize (datetimes, custom objects) — you must supply `default=` or a custom encoder.
- **`DictReader` handles ragged rows gracefully**: missing trailing fields become `None`; extra fields beyond the header get collected under the `restkey` name instead of raising an error.
- Always open CSV files with `newline=""` on write — otherwise you can get extra blank lines on some platforms.
- JSON has no native "date" type — always serialize datetimes as ISO strings (`.isoformat()`) and parse them back manually.

## When it matters
JSON: talking to APIs, reading/writing config files. CSV: importing/exporting spreadsheet-style tabular data, or ingesting messy/malformed exports where `DictReader`'s tolerance saves manual cleanup.

## One-line recap example
```python
import json
from datetime import datetime
data = {"when": datetime.now()}
print(json.dumps(data, default=lambda o: o.isoformat()))  # handles non-serializable types
```
