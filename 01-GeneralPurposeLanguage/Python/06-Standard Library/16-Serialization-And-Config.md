# Serialization and Config — Notes

## What this covers
Saving Python data to disk/network (`pickle`, `shelve`, `json` + dataclasses) and reading settings from files and the environment (`configparser`, `tomllib`, `os.environ`), plus layering config and versioning saved data.

## Key points
- **Serialization** = object -> bytes/text -> object again. **Config** = settings kept outside the code.
- **`pickle`**: `dumps/loads` (bytes), `dump/load` (binary files, `'wb'`/`'rb'`). Handles sets, tuples, custom classes — things `json` can't.
- Protocols: default is 4, highest is 5 (3.8+). Higher = smaller/faster but older Pythons may not read it (`protocol=` to choose).
- Can't pickle: lambdas, nested functions, open files, locks, sockets. pickle saves objects **by name**, not by code.
- Custom classes: `__dict__` + class name are saved; `__init__` is **not** run on load. `__getstate__` / `__setstate__` drop and rebuild things like locks or caches.
- **Security**: unpickling can run code (via `__reduce__`). The demo makes `loads()` call `print` — a real attacker would call something harmful. Never unpickle untrusted data.
- **pickle vs json**: json = text, safe, any language, few types. pickle = binary, Python-only, any object, unsafe on untrusted data. Default to json.
- **`shelve`**: a dict stored on disk (values pickled automatically). Keys must be `str`. Use `with shelve.open(path) as db:` so it closes.
- `marshal` is only the internal `.pyc` format (not stable, not for you). `copyreg` registers pickling for types you can't edit (advanced).
- **Dataclasses + json**: `asdict()` / `astuple()` give plain data json can write. Rebuild nested dataclasses by hand, or use `default=` (encode with a `"__type__"` tag) and `object_hook=` (decode from a fixed registry of classes).
- **`configparser`** (INI): `[sections]`, `key = value`. Read with `read()` / `read_string()`; convert with `getint`, `getfloat`, `getboolean` (`yes/true/on/1`). `fallback=` for optional keys.
- `[DEFAULT]` values are inherited by every section.
- Interpolation: `%(name)s` (same section/DEFAULT) by default; `ExtendedInterpolation` uses `${section:key}`; `interpolation=None` disables it.
- **`tomllib`** (3.11+): read-only TOML with real types (int, bool, lists, tables). `load()` needs a file opened `"rb"`. Writing TOML needs the third-party `tomli-w`.
- **Environment variables** (`os.environ`, `os.getenv`): the 12-factor home for per-deploy settings and secrets. Values are always strings.
- **Layered config**: `ChainMap(cli, env, file, defaults)` — strongest layer first; later layers only fill gaps.
- **Versioning**: save a `"version"` field; on load, run small migration steps (`v1->v2->v3`) until current. Reject files from a newer version.
- Format cheat sheet: json (readable, safe, basic types), pickle/shelve (binary, unsafe, any object), ini (readable, safe, strings), toml (readable, safe, typed), csv (readable, safe, strings).

## Gotchas (the part worth revising twice)
- `pickle.loads` on data you didn't create = running someone else's code. `hmac` signing proves origin, not safety.
- Old pickles break if you rename or move the class.
- `shelve`: `db["k"].append(x)` changes a temporary copy and is **lost** — reassign (`db["k"] = rec`) or open with `writeback=True` (slower, caches in memory). Non-`str` keys fail.
- `configparser` lowercases keys (`Name` -> `name`) and every value is a string. A bare `%` in a value raises `InterpolationSyntaxError` — write `%%` or turn interpolation off. Set `parser.optionxform = str` to keep key case.
- `bool("false")` is `True`! Parse env flags yourself (`value.lower() in ("1", "true", "yes")`) and convert ports/ints with `int()`.
- `os.environ["X"] = 5` raises `TypeError` — values must be `str`. Changes affect only the current process.
- `ChainMap` order is strongest-first, and writes go to the **first** map only.
- `tomllib.load(open(p))` (text mode) fails — use `"rb"`.
- `json.dumps(dataclass_instance)` raises `TypeError`; convert with `asdict()` first.
- Never commit secrets into a config file in git — use env vars or a secrets manager.

## When it matters
App settings that differ between laptop/staging/production, caching expensive results to disk, saving user progress/profiles that must keep loading after you ship a new version, and any time you're tempted to `pickle.load` a file you didn't write.

## One-line recap example
```python
import json
from dataclasses import dataclass, asdict
@dataclass
class P: name: str
print(json.dumps(asdict(P("Ana"))))   # {"name": "Ana"}  -> dataclass -> dict -> safe JSON text
```
