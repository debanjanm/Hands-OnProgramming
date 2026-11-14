import json
import csv
import os

# 01. json and csv Modules - Introduction
# ------------------------------------
# - json: read/write JSON data (common for APIs and config files).
# - csv: read/write CSV (comma-separated values) files (common for tabular data).

print("# 01. json and csv Modules - Introduction")
print("# ------------------------------------")

# 02. json.dumps() - Python Object to JSON String
# ------------------------------------
data = {"name": "Debanjan", "age": 25, "skills": ["Python", "SQL"], "active": True}
json_string = json.dumps(data, indent=2)
print("\n# 02. json.dumps()")
print(json_string)

# 03. json.loads() - JSON String to Python Object
# ------------------------------------
parsed = json.loads(json_string)
print("\n# 03. json.loads()")
print(parsed)
print("type:", type(parsed))
print("name:", parsed["name"])

# 04. json.dump() and json.load() - Working with Files
# ------------------------------------
print("\n# 04. json.dump() and json.load() - Files")
with open("temp_data.json", "w") as f:
    json.dump(data, f, indent=2)

with open("temp_data.json", "r") as f:
    loaded = json.load(f)
print("loaded from file:", loaded)

# 05. Handling Nested JSON
# ------------------------------------
nested = {
    "user": {"name": "Debanjan", "address": {"city": "Kolkata", "zip": "700001"}},
    "orders": [{"id": 1, "total": 250}, {"id": 2, "total": 99}],
}
print("\n# 05. Handling Nested JSON")
print("city:", nested["user"]["address"]["city"])
print("first order total:", nested["orders"][0]["total"])

# 06. csv.writer() - Writing CSV Files
# ------------------------------------
rows = [
    ["Name", "Age", "City"],
    ["Debanjan", 25, "Kolkata"],
    ["Asha", 30, "Mumbai"],
]
print("\n# 06. csv.writer()")
with open("temp_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)
print("CSV file written")

# 07. csv.reader() - Reading CSV Files
# ------------------------------------
print("\n# 07. csv.reader()")
with open("temp_data.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)

# 08. csv.DictWriter() and csv.DictReader() - Row as Dict
# ------------------------------------
people = [
    {"Name": "Debanjan", "Age": 25, "City": "Kolkata"},
    {"Name": "Asha", "Age": 30, "City": "Mumbai"},
]
print("\n# 08. csv.DictWriter() and csv.DictReader()")
with open("temp_data_dict.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Age", "City"])
    writer.writeheader()
    writer.writerows(people)

with open("temp_data_dict.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(dict(row))

# 09. Cleanup
# ------------------------------------
os.remove("temp_data.json")
os.remove("temp_data.csv")
os.remove("temp_data_dict.csv")
print("\n# 09. Cleanup")
print("temp files removed")

# 10. Custom JSON Encoder for Non-Serializable Types
# ------------------------------------
# - json.dumps() doesn't know how to serialize datetime, custom classes, etc.
#   Fix it with a `default=` function or a json.JSONEncoder subclass.
from datetime import datetime

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

def json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Point):
        return {"x": obj.x, "y": obj.y}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

event = {"name": "launch", "when": datetime(2026, 8, 2, 9, 0), "at": Point(3, 4)}
print("\n# 10. Custom JSON Encoder (default=)")
print(json.dumps(event, default=json_default, indent=2))

class CustomEncoder(json.JSONEncoder):  # equivalent, as a reusable subclass
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Point):
            return {"x": obj.x, "y": obj.y}
        return super().default(obj)

print(json.dumps(event, cls=CustomEncoder))

# 11. sort_keys and separators - Deterministic, Compact Output
# ------------------------------------
messy = {"b": 2, "a": 1, "c": 3}
print("\n# 11. sort_keys and separators")
print("sorted:", json.dumps(messy, sort_keys=True))
print("compact:", json.dumps(messy, separators=(",", ":")))  # no extra spaces

# 12. CSV Dialects - excel vs Custom Delimiter/Quotechar
# ------------------------------------
print("\n# 12. CSV Dialects")
csv.register_dialect("pipes", delimiter="|", quotechar="'")
with open("temp_pipes.csv", "w", newline="") as f:
    writer = csv.writer(f, dialect="pipes")
    writer.writerow(["Name", "City"])
    writer.writerow(["Debanjan", "Kolkata"])

with open("temp_pipes.csv", "r") as f:
    print("raw file content:", f.read().strip())
with open("temp_pipes.csv", "r") as f:
    for row in csv.reader(f, dialect="pipes"):
        print("parsed row:", row)

# 13. Handling Malformed/Missing CSV Fields Gracefully
# ------------------------------------
# - DictReader fills missing trailing fields with None; extra fields are
#   collected under the `restkey` name instead of raising an error.
ragged_csv = "Name,Age,City\nDebanjan,25,Kolkata\nAsha,30\nRaj,40,Mumbai,India\n"
with open("temp_ragged.csv", "w") as f:
    f.write(ragged_csv)

print("\n# 13. Malformed/Missing CSV Fields")
with open("temp_ragged.csv", "r") as f:
    reader = csv.DictReader(f, restkey="extra")
    for row in reader:
        print(dict(row))

# 14. csv.Sniffer - Detect Dialect From a Sample
# ------------------------------------
print("\n# 14. csv.Sniffer")
with open("temp_pipes.csv", "r") as f:
    sample = f.read()
detected = csv.Sniffer().sniff(sample)
print("detected delimiter:", repr(detected.delimiter))
print("has header:", csv.Sniffer().has_header(sample))

# 15. Cleanup (extra files from this section)
# ------------------------------------
os.remove("temp_pipes.csv")
os.remove("temp_ragged.csv")
print("\n# 15. Cleanup")
print("extra temp files removed")
