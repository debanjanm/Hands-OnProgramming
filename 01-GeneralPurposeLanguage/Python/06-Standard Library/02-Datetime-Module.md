# Datetime Module — Notes

## What this covers
The `datetime` module's core classes (`date`, `time`, `datetime`, `timedelta`) for representing dates/times, plus timezone handling with `zoneinfo`.

## Key points
- **`date`**, **`time`**, **`datetime`** — date-only, time-only, and combined date+time. `.today()` / `.now()` get the current value.
- **`timedelta`** — a duration (`timedelta(days=7, hours=3)`). Add/subtract it from dates, or subtract two dates to get one.
- **`strftime()`** — datetime → string (`now.strftime("%Y-%m-%d")`). **`strptime()`** — string → datetime, using the same format codes.
- **Common format codes** — `%Y`/`%y` year, `%m` month, `%d` day, `%H`/`%I` hour (24h/12h), `%M` minute, `%S` second, `%A`/`%B` weekday/month name, `%p` AM/PM.
- **Comparing dates** — normal operators (`>`, `min()`) work directly on `date`/`datetime` objects.
- **`isoformat()` / `fromisoformat()`** — round-trip to/from the standard `YYYY-MM-DD` string format.
- **`zoneinfo.ZoneInfo`** (3.9+) — attach a real timezone via `tzinfo=ZoneInfo("Asia/Kolkata")`, making a datetime "aware" instead of "naive".
- **`.astimezone()`** — convert an aware datetime to a different timezone.
- **`.timestamp()` / `datetime.fromtimestamp()`** — convert to/from Unix epoch seconds.
- **`calendar` module** (brief) — `calendar.monthrange(year, month)` gives first weekday + days in month; `calendar.isleap(year)` checks leap years.

## Gotchas (the part worth revising twice)
- **Naive vs aware datetimes cannot be compared** — mixing a plain `datetime(...)` (no tzinfo) with a `ZoneInfo`-attached one raises `TypeError`, not a silent wrong answer. Always know which kind you're holding.
- A "naive" datetime has no timezone attached at all — it doesn't mean "assume UTC", it means "timezone unknown".
- `strftime` and `strptime` are easy to confuse: **f**ormat = datetime→string, **p**arse = string→datetime.
- Regular dicts/objects print misleadingly close-looking dates; always check `.tzinfo` if a bug smells timezone-related.

## When it matters
Any time you're logging timestamps, scheduling, comparing dates across users in different timezones, or parsing dates from files/APIs.

## One-line recap example
```python
from datetime import datetime
from zoneinfo import ZoneInfo
aware = datetime.now(tz=ZoneInfo("UTC"))   # always attach a timezone for real apps
print(aware.strftime("%Y-%m-%d %H:%M %Z"))
```
