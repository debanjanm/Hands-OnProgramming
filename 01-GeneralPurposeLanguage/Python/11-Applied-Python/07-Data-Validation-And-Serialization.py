# 01. json Basics: dumps / loads
# 02. dumps Options: indent, sort_keys, separators, ensure_ascii
# 03. What JSON Cannot Represent
# 04. Custom Encoders: default= and JSONEncoder
# 05. Custom Decoding: object_hook
# 06. Dates and Decimal
# 07. dataclasses + asdict
# 08. Validation in __post_init__
# 09. pydantic v2: BaseModel and Field Constraints
# 10. pydantic Validators
# 11. pydantic: model_dump / model_validate / JSON
# 12. pydantic: Nested Models and Discriminated Unions
# 13. Settings from Environment
# 14. csv Round-Trip
# 15. tomllib and yaml
# 16. JSON Schema and a Tiny Validator
# 17. Parse, Don't Validate
# 18. Never Unpickle Untrusted Data
# 19. Error-Message Design

import csv
import io
import json
import os
import tomllib
from dataclasses import dataclass, asdict, field
from datetime import date, datetime
from decimal import Decimal

try:
    import pydantic
    from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
    HAVE_PYDANTIC = True
except ImportError:
    HAVE_PYDANTIC = False

try:
    import yaml
except ImportError:
    yaml = None

# 01. json Basics: dumps / loads
# ----------------------------
# - dumps(obj) -> str, loads(str) -> obj. dump/load do the same with files.
# - Mapping: dict<->object, list/tuple->array, str, int/float, True/False->true/false, None->null.

data = {"name": "Asha", "age": 30, "tags": ["a", "b"], "active": True, "boss": None}
text = json.dumps(data)
print(text)
print(json.loads(text) == data)
print(json.loads('[1, 2.5, "x", null, true]'))

# 02. dumps Options: indent, sort_keys, separators, ensure_ascii
# ----------------------------
# - indent=2 pretty prints; sort_keys=True makes output stable (good for diffs/hashes).
# - separators=(",", ":") gives the most compact form.
# - ensure_ascii=False keeps non-ASCII characters readable instead of \uXXXX.

d = {"b": 1, "a": {"z": [1, 2], "y": "café"}}
print(json.dumps(d, indent=2, sort_keys=True))
print(json.dumps(d, separators=(",", ":"), sort_keys=True))
print(json.dumps(d, sort_keys=True))
print(json.dumps(d, sort_keys=True, ensure_ascii=False))

# 03. What JSON Cannot Represent
# ----------------------------
# - set, bytes, datetime, Decimal, custom objects -> TypeError.
# - Tuples become lists; dict keys become strings (int key 1 -> "1").
# - NaN / Infinity are written by default but are NOT valid JSON; allow_nan=False refuses.

try:
    json.dumps({"s": {1, 2}})
except TypeError as e:
    print("TypeError:", e)
print(json.loads(json.dumps({1: "a", "t": (1, 2)})))
print(json.dumps(float("nan")))
try:
    json.dumps(float("nan"), allow_nan=False)
except ValueError as e:
    print("ValueError:", e)
try:
    json.loads("{'single': 'quotes'}")
except json.JSONDecodeError as e:
    print("JSONDecodeError:", e.msg, "at line", e.lineno, "col", e.colno)

# 04. Custom Encoders: default= and JSONEncoder
# ----------------------------
# - default(obj) is called ONLY for objects json does not know. Return something
#   json can handle, or raise TypeError.
# - Subclass JSONEncoder when you want a reusable encoder (cls=MyEncoder).

def fallback(obj):
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"cannot serialise {type(obj).__name__}")

print(json.dumps({"s": {3, 1, 2}}, default=fallback))

class AppEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, set):
            return sorted(o)
        return super().default(o)  # raises TypeError for the rest

print(json.dumps({"when": date(2024, 1, 31), "price": Decimal("19.99")}, cls=AppEncoder))

# 05. Custom Decoding: object_hook
# ----------------------------
# - object_hook(dict) is called for EVERY decoded JSON object (innermost first).
# - Use it to rebuild types, usually by looking for a marker key like "__type__".

def tag_encode(o):
    if isinstance(o, complex):
        return {"__type__": "complex", "re": o.real, "im": o.imag}
    raise TypeError

def tag_decode(d):
    if d.get("__type__") == "complex":
        return complex(d["re"], d["im"])
    return d

s = json.dumps({"z": 1 + 2j}, default=tag_encode)
print(s)
print(json.loads(s, object_hook=tag_decode))
# parse_float / parse_int hooks change how numbers are read
print(json.loads('{"p": 0.1}', parse_float=Decimal))

# 06. Dates and Decimal
# ----------------------------
# - JSON has no date type: store ISO 8601 strings and convert back yourself.
# - Float money is lossy. Write Decimal as a STRING, read with Decimal(str).
# - Decoding with parse_float=Decimal keeps exact digits of JSON numbers.

print(0.1 + 0.2, Decimal("0.1") + Decimal("0.2"))
payload = json.dumps({"d": date(2024, 3, 5), "amt": Decimal("10.10")}, cls=AppEncoder)
back = json.loads(payload)
print(back)
print(date.fromisoformat(back["d"]) + (date(2024, 3, 6) - date(2024, 3, 5)))
print(Decimal(back["amt"]) * 3)
print(datetime.fromisoformat("2024-03-05T10:30:00").hour)

# 07. dataclasses + asdict
# ----------------------------
# - asdict(obj) recursively converts a dataclass (and nested ones) into dicts/lists.
# - Rebuild with Cls(**d); nested objects need manual rebuilding.
# - asdict does NOT convert dates/Decimals - the encoder still has to.

@dataclass
class Address:
    city: str
    zip: str

@dataclass
class User:
    name: str
    age: int
    address: Address
    tags: list = field(default_factory=list)

u = User("Ravi", 41, Address("Pune", "411001"), ["x"])
dd = asdict(u)
print(dd)
u2 = User(**{**dd, "address": Address(**dd["address"])})
print(u2 == u)

# 08. Validation in __post_init__
# ----------------------------
# - Dataclasses do NOT check types at runtime: User(age="oops") is accepted.
# - __post_init__ runs right after __init__: validate (or convert) there.

@dataclass
class Product:
    name: str
    price: Decimal
    qty: int = 1

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("name must not be blank")
        self.price = Decimal(str(self.price))  # normalise
        if self.price < 0:
            raise ValueError(f"price must be >= 0, got {self.price}")
        if not isinstance(self.qty, int) or isinstance(self.qty, bool):
            raise TypeError(f"qty must be int, got {type(self.qty).__name__}")

print(Product("pen", 1.5))
for kwargs in ({"name": " ", "price": 1}, {"name": "x", "price": -2}, {"name": "x", "price": 1, "qty": "3"}):
    try:
        Product(**kwargs)
    except (ValueError, TypeError) as e:
        print(type(e).__name__ + ":", e)
print(User("A", "not-an-int", Address("c", "z")).age, "<- dataclass alone never checks types")

# 09. pydantic v2: BaseModel and Field Constraints
# ----------------------------
# - BaseModel validates AND converts ("lax mode": "5" -> 5) on creation.
# - Field(...) adds constraints: gt, ge, lt, le, min_length, max_length, pattern.
# - Errors are collected: ValidationError lists every bad field, not just the first.

if HAVE_PYDANTIC:
    class Item(BaseModel):
        name: str = Field(min_length=2, max_length=20)
        price: float = Field(gt=0)
        qty: int = Field(default=1, ge=1, le=100)
        sku: str = Field(default="AB-123", pattern=r"^[A-Z]{2}-\d{3}$")

    print(Item(name="pen", price="2.5", qty="3"))  # strings coerced
    try:
        Item(name="x", price=-1, qty=500, sku="bad")
    except ValidationError as e:
        print(e.error_count(), "errors")
        for err in e.errors():
            print(" ", err["loc"], err["type"], "->", err["msg"])
else:
    print("skip: pydantic not installed")

# 10. pydantic Validators
# ----------------------------
# - @field_validator("f") checks/normalises one field (mode="before" runs pre-parse).
# - @model_validator(mode="after") checks relations between fields.
# - Raise ValueError (or AssertionError) -> becomes a ValidationError entry.

if HAVE_PYDANTIC:
    class Booking(BaseModel):
        email: str
        start: date
        end: date

        @field_validator("email")
        @classmethod
        def lower_and_check(cls, v: str) -> str:
            v = v.strip().lower()
            if "@" not in v:
                raise ValueError("must contain @")
            return v

        @model_validator(mode="after")
        def check_order(self):
            if self.end < self.start:
                raise ValueError("end must not be before start")
            return self

    print(Booking(email="  A@B.com ", start="2024-01-01", end="2024-01-05"))
    try:
        Booking(email="nope", start="2024-02-01", end="2024-01-01")
    except ValidationError as e:
        for err in e.errors():
            print(" ", err["loc"], "->", err["msg"])
else:
    print("skip: pydantic not installed")

# 11. pydantic: model_dump / model_validate / JSON
# ----------------------------
# - model_dump() -> dict; model_dump(mode="json") -> JSON-safe dict (dates as strings).
# - model_dump_json() -> str; model_validate(dict) and model_validate_json(str) go back.
# - model_json_schema() gives a JSON Schema for free.

if HAVE_PYDANTIC:
    class Event(BaseModel):
        title: str
        day: date
        cost: Decimal = Decimal("0")

    ev = Event(title="Meetup", day="2024-05-01", cost="12.50")
    print(ev.model_dump())
    print(ev.model_dump(mode="json"))
    js = ev.model_dump_json()
    print(js)
    print(Event.model_validate_json(js) == ev)
    print(Event.model_validate({"title": "T", "day": date(2024, 1, 1)}))
    print(ev.model_dump(exclude={"cost"}))
    print(sorted(Event.model_json_schema()["properties"]))
else:
    print("skip: pydantic not installed")

# 12. pydantic: Nested Models and Discriminated Unions
# ----------------------------
# - A field typed as another model is validated recursively; error locs show the path.
# - Union[Cat, Dog] guesses; a DISCRIMINATED union picks by a tag field: faster and
#   gives precise errors.

if HAVE_PYDANTIC:
    from typing import Literal, Union
    from typing import Annotated

    class Cat(BaseModel):
        kind: Literal["cat"]
        lives: int

    class Dog(BaseModel):
        kind: Literal["dog"]
        good_boy: bool

    class Owner(BaseModel):
        name: str
        pet: Annotated[Union[Cat, Dog], Field(discriminator="kind")]

    print(Owner.model_validate({"name": "Mo", "pet": {"kind": "dog", "good_boy": "yes"}}))
    print(Owner.model_validate_json('{"name": "Jo", "pet": {"kind": "cat", "lives": 9}}'))
    try:
        Owner.model_validate({"name": "X", "pet": {"kind": "fish"}})
    except ValidationError as e:
        print(e.errors()[0]["loc"], e.errors()[0]["type"])
    try:
        Owner.model_validate({"name": "X", "pet": {"kind": "cat", "lives": "many"}})
    except ValidationError as e:
        print(e.errors()[0]["loc"], e.errors()[0]["type"])
else:
    print("skip: pydantic not installed")

# 13. Settings from Environment
# ----------------------------
# - 12-factor style: configuration comes from environment variables.
# - pydantic-settings (separate package) does this declaratively; otherwise
#   read os.environ yourself and convert types explicitly. Env values are ALWAYS strings.

os.environ["DEMO_APP_PORT"] = "8080"
os.environ["DEMO_APP_DEBUG"] = "true"
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="DEMO_APP_")
        port: int = 80
        debug: bool = False
        name: str = "svc"

    print("pydantic-settings:", Settings())
except ImportError:
    print("pydantic-settings not installed, using os.environ")

    def load_settings(env=os.environ):
        return {
            "port": int(env.get("DEMO_APP_PORT", "80")),
            "debug": env.get("DEMO_APP_DEBUG", "false").lower() in ("1", "true", "yes"),
            "name": env.get("DEMO_APP_NAME", "svc"),
        }

    print(load_settings())
os.environ.pop("DEMO_APP_PORT")
os.environ.pop("DEMO_APP_DEBUG")
print("bool('false') is", bool("false"), "<- never bool() an env string")

# 14. csv Round-Trip
# ----------------------------
# - Use csv, not str.split(","): it handles quotes, commas and newlines inside fields.
# - Open real files with newline="" ; here io.StringIO stands in for a file.
# - EVERYTHING read back is a string: convert types yourself.

rows = [{"name": "Asha, K.", "score": 91, "note": 'said "hi"'}, {"name": "Bo", "score": 7, "note": ""}]
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=["name", "score", "note"], lineterminator="\n")
w.writeheader()
w.writerows(rows)
print(buf.getvalue(), end="")
buf.seek(0)
back = list(csv.DictReader(buf))
print(back)
print([{**r, "score": int(r["score"])} for r in back] == rows)

# 15. tomllib and yaml
# ----------------------------
# - tomllib (3.11+, stdlib) is READ-ONLY: loads(str) / load(binary file). No dump.
# - PyYAML: use safe_load / safe_dump. Plain yaml.load can build arbitrary objects.
# - YAML gotcha: unquoted 'no', 'yes', 'on', 'off' become booleans (the Norway problem).

cfg = tomllib.loads('''
title = "demo"
[server]
port = 8000
hosts = ["a", "b"]
''')
print(cfg)
if yaml is not None:
    y = yaml.safe_dump(cfg, sort_keys=True)
    print(y, end="")
    print(yaml.safe_load(y) == cfg)
    print(yaml.safe_load("country: no"))
else:
    print("skip: PyYAML not installed")

# 16. JSON Schema and a Tiny Validator
# ----------------------------
# - JSON Schema describes the shape of JSON as JSON: type, required, properties,
#   minimum, enum, items...
# - The real library is `jsonschema`; below is a tiny validator covering the basics
#   so you see the idea. Collect ALL errors with a path to each.

TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict, "null": type(None)}

def validate(value, schema, path="$"):
    errors = []
    t = schema.get("type")
    if t:
        ok = isinstance(value, TYPES[t])
        if t in ("integer", "number") and isinstance(value, bool):
            ok = False
        if not ok:
            return [f"{path}: expected {t}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not one of {schema['enum']}")
    if "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path}: {value} is below minimum {schema['minimum']}")
    if "minLength" in schema and len(value) < schema["minLength"]:
        errors.append(f"{path}: shorter than {schema['minLength']} characters")
    if t == "object":
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required key '{key}'")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                errors += validate(value[key], sub, f"{path}.{key}")
    if t == "array" and "items" in schema:
        for i, item in enumerate(value):
            errors += validate(item, schema["items"], f"{path}[{i}]")
    return errors

SCHEMA = {
    "type": "object",
    "required": ["name", "age"],
    "properties": {
        "name": {"type": "string", "minLength": 2},
        "age": {"type": "integer", "minimum": 0},
        "role": {"enum": ["admin", "user"]},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}
print(validate({"name": "Asha", "age": 3, "tags": ["x"]}, SCHEMA))
for e in validate({"name": "A", "age": -1, "role": "root", "tags": ["ok", 5]}, SCHEMA):
    print(" ", e)
print(validate({"age": True}, SCHEMA))

# 17. Parse, Don't Validate
# ----------------------------
# - Validating = checking and then keeping the raw data (you must re-check later).
# - Parsing = turning raw data into a TYPE that can only exist when valid.
# - Do it once at the boundary; the rest of the code trusts the type.

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        v = self.value.strip().lower()
        local, _, domain = v.partition("@")
        if not local or "." not in domain:
            raise ValueError(f"not an email address: {self.value!r}")
        object.__setattr__(self, "value", v)  # frozen: bypass for normalising

def send_welcome(to: Email) -> str:
    return "would email " + to.value  # no re-checking needed

print(send_welcome(Email("  Dev@Example.COM ")))
try:
    Email("nonsense")
except ValueError as e:
    print("rejected:", e)

# 18. Never Unpickle Untrusted Data
# ----------------------------
# - pickle can run ARBITRARY code while loading (via __reduce__). Loading a pickle
#   from a user, network or shared file = letting them run code on your machine.
# - For data from outside, use JSON (or another data-only format).
# - Below we only SHOW that a pickle records a callable; we never load it.

import pickle
import pickletools

class Evil:
    def __reduce__(self):
        return (print, ("this would run on load",))

blob = pickle.dumps(Evil())
ops = [op.name for op, _, _ in pickletools.genops(blob)]
print("pickle stream contains a call opcode:", "REDUCE" in ops)
print("safe alternative:", json.loads(json.dumps({"just": "data"})))

# 19. Error-Message Design
# ----------------------------
# - A good message says: WHERE (field path), WHAT was wrong, WHAT is expected,
#   and (carefully) what was received.
# - Report all problems at once, not one per run.
# - Never echo secrets (passwords, tokens) back in an error.

bad = "Invalid input"
good = "user.age: expected integer >= 0, got -5"
print("bad :", bad)
print("good:", good)

def mask(v: str) -> str:
    return v[:2] + "*" * (len(v) - 2)

print("safe echo of a secret:", mask("hunter2xyz"))
print("many at once:", len(validate({"name": "", "age": "x", "role": "z"}, SCHEMA)), "problems reported together")
