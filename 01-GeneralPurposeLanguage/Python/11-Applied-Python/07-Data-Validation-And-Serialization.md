# Data Validation and Serialization — Notes

## What this covers
Turning Python data into text and back (json, csv, tomllib, yaml), checking that incoming data is valid (dataclass `__post_init__`, pydantic v2, a tiny JSON Schema validator), and the safety rules around untrusted data.

## Key points
- `json.dumps/loads` work on strings, `dump/load` on files. Useful options: `indent`, `sort_keys`, `separators`, `ensure_ascii=False`.
- JSON only knows dict, list, str, number, bool, null. Anything else needs `default=` / a `JSONEncoder` subclass on the way out and `object_hook` (or manual conversion) on the way in.
- Dates go as ISO 8601 strings; money goes as a `Decimal` stored as a string (or read with `parse_float=Decimal`).
- `dataclasses.asdict` converts recursively; dataclasses do not check types, so validate in `__post_init__`.
- pydantic v2: `BaseModel` + `Field(gt=, min_length=, pattern=)`, `@field_validator`, `@model_validator`, `model_dump`, `model_validate`, `model_validate_json`, nested models, discriminated unions (`Field(discriminator="kind")`), `model_json_schema()`.
- Settings come from environment variables (strings!): `pydantic-settings` if installed, else `os.environ` plus explicit conversion.
- `csv` handles quoting; everything read back is a string. `tomllib` is read-only. Use `yaml.safe_load`.
- Parse, don't validate: convert raw input into a type that can only exist when valid, once, at the boundary.
- Good error messages give the path, the problem, the expectation, and report all problems at once.

## Gotchas (the part worth revising twice)
- `json.dumps` of a `set`, `datetime`, `Decimal` raises `TypeError`; int dict keys silently become strings; tuples come back as lists.
- `NaN`/`Infinity` are emitted by default but are not valid JSON — use `allow_nan=False` to catch them.
- Floats for money: `0.1 + 0.2 != 0.3`. Use `Decimal` built from strings.
- `User(age="oops")` works on a plain dataclass — no runtime type checks.
- pydantic is lax by default: `"5"` becomes `5`. Use strict mode if you need exact types.
- `bool("false")` is `True`. Parse env strings explicitly.
- YAML `no`/`yes`/`on`/`off` become booleans (the "Norway problem"); use `safe_load`, never `load`.
- `pickle.loads` on untrusted data can run arbitrary code. Use JSON for data from outside.
- csv files need `newline=""` when opened for real.

## When it matters
Every API, config file, form and file import. Validate at the edge, trust the types inside, and fail with messages a user can act on.

## One-line recap example
```python
import json
from pydantic import BaseModel

class P(BaseModel):
    name: str
    age: int

print(P.model_validate_json('{"name": "Asha", "age": "30"}').model_dump_json())
```
