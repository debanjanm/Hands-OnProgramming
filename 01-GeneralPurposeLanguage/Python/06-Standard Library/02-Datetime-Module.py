from datetime import date, time, datetime, timedelta

# 01. datetime Module - Introduction
# ------------------------------------
# - Provides classes for working with dates, times, and time intervals.
# - Main classes: date, time, datetime, timedelta.

print("# 01. datetime Module - Introduction")
print("# ------------------------------------")

# 02. date - Working with Dates
# ------------------------------------
today = date.today()
print("\n# 02. date")
print("today:", today)
print("year:", today.year, "month:", today.month, "day:", today.day)

specific_date = date(2025, 12, 25)
print("specific date:", specific_date)
print("weekday (0=Mon):", specific_date.weekday())

# 03. time - Working with Time (no date component)
# ------------------------------------
t = time(14, 30, 15)
print("\n# 03. time")
print("time:", t)
print("hour:", t.hour, "minute:", t.minute, "second:", t.second)

# 04. datetime - Combined Date and Time
# ------------------------------------
now = datetime.now()
print("\n# 04. datetime")
print("now:", now)

specific_dt = datetime(2026, 1, 1, 9, 0, 0)
print("specific datetime:", specific_dt)

# 05. timedelta - Representing Durations
# ------------------------------------
delta = timedelta(days=7, hours=3)
print("\n# 05. timedelta")
print("delta:", delta)

one_week_later = today + delta
print("today + 7 days 3 hours:", one_week_later)

difference = specific_date - today
print("days until specific_date:", difference.days)

# 06. Formatting Dates - strftime() (datetime -> string)
# ------------------------------------
print("\n# 06. strftime() - datetime to string")
print(now.strftime("%Y-%m-%d"))          # 2026-08-02
print(now.strftime("%d/%m/%Y"))          # 02/08/2026
print(now.strftime("%A, %B %d, %Y"))     # Sunday, August 02, 2026
print(now.strftime("%H:%M:%S"))          # 14:30:15

# 07. Parsing Dates - strptime() (string -> datetime)
# ------------------------------------
print("\n# 07. strptime() - string to datetime")
parsed = datetime.strptime("2025-12-25", "%Y-%m-%d")
print(parsed)

parsed2 = datetime.strptime("25/12/2025 14:30", "%d/%m/%Y %H:%M")
print(parsed2)

# 08. Comparing Dates
# ------------------------------------
print("\n# 08. Comparing Dates")
print("specific_date > today:", specific_date > today)
print("earliest:", min(today, specific_date))

# 09. Common strftime Format Codes (reference)
# ------------------------------------
print("\n# 09. Common strftime Format Codes (reference)")
print("# %Y=year(4d) %y=year(2d) %m=month %d=day")
print("# %H=hour(24h) %I=hour(12h) %M=minute %S=second")
print("# %A=weekday name %B=month name %p=AM/PM")

# 10. Timezone-Aware Datetimes with zoneinfo (Python 3.9+)
# ------------------------------------
# - A "naive" datetime (like `now` above) has no timezone attached.
# - An "aware" datetime knows which timezone it represents.
from zoneinfo import ZoneInfo

kolkata = datetime(2026, 8, 2, 14, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
print("\n# 10. Timezone-Aware Datetimes (zoneinfo)")
print("aware datetime:", kolkata)
print("tzinfo:", kolkata.tzinfo)
print("utc offset:", kolkata.utcoffset())

# 11. Converting Between Timezones
# ------------------------------------
new_york = kolkata.astimezone(ZoneInfo("America/New_York"))
utc = kolkata.astimezone(ZoneInfo("UTC"))
print("\n# 11. Converting Between Timezones")
print("Kolkata:", kolkata)
print("New York:", new_york)
print("UTC:", utc)

# 12. Naive vs Aware - the Comparison Gotcha
# ------------------------------------
# - You cannot compare a naive datetime with an aware one - Python raises
#   TypeError instead of guessing what you meant.
naive_dt = datetime(2026, 8, 2, 14, 30)
print("\n# 12. Naive vs Aware Gotcha")
try:
    naive_dt < kolkata
except TypeError as e:
    print("TypeError:", e)

# 13. Unix Timestamps - timestamp() and fromtimestamp()
# ------------------------------------
print("\n# 13. Unix Timestamps")
ts = kolkata.timestamp()          # datetime -> seconds since epoch (float)
print("timestamp:", ts)
back_to_dt = datetime.fromtimestamp(ts, tz=ZoneInfo("Asia/Kolkata"))
print("timestamp -> datetime:", back_to_dt)

# 14. date.isoformat() and date.fromisoformat()
# ------------------------------------
print("\n# 14. date.isoformat() / fromisoformat()")
iso_str = today.isoformat()       # 'YYYY-MM-DD', the standard ISO 8601 format
print("isoformat:", iso_str)
back_to_date = date.fromisoformat(iso_str)
print("fromisoformat:", back_to_date, "| equal to today:", back_to_date == today)

# 15. calendar Module (brief mention)
# ------------------------------------
import calendar

print("\n# 15. calendar Module (brief mention)")
weekday, days_in_month = calendar.monthrange(2026, 2)  # (year, month)
print("Feb 2026: first weekday (0=Mon):", weekday, "| days in month:", days_in_month)
print("is leap year:", calendar.isleap(2026))
