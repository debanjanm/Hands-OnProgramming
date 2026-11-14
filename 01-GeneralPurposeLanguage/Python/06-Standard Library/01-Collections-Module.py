from collections import Counter, defaultdict, deque, namedtuple, OrderedDict, ChainMap

# 01. collections Module - Introduction
# ------------------------------------
# - Provides specialized container datatypes as alternatives to Python's
#   general-purpose built-ins (dict, list, set, tuple).

print("# 01. collections Module - Introduction")
print("# ------------------------------------")

# 02. Counter - Counting Hashable Objects
# ------------------------------------
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counts = Counter(words)
print("\n# 02. Counter")
print(counts)
print("most common:", counts.most_common(2))
print("count of 'apple':", counts["apple"])
print("count of missing key (no KeyError):", counts["mango"])

# 03. defaultdict - Dict with Default Values
# ------------------------------------
groups = defaultdict(list)
pairs = [("fruit", "apple"), ("veg", "carrot"), ("fruit", "banana")]
for category, item in pairs:
    groups[category].append(item)
print("\n# 03. defaultdict")
print(dict(groups))

word_lengths = defaultdict(int)
for word in words:
    word_lengths[word] += 1
print(dict(word_lengths))

# 04. deque - Double-Ended Queue
# ------------------------------------
# - Fast O(1) appends/pops from both ends (list is O(n) at the front).
dq = deque([1, 2, 3])
dq.append(4)       # add to right
dq.appendleft(0)   # add to left
print("\n# 04. deque")
print(dq)
dq.pop()           # remove from right
dq.popleft()       # remove from left
print(dq)

dq.rotate(1)
print("rotated right:", dq)

# 05. namedtuple - Tuples with Named Fields
# ------------------------------------
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print("\n# 05. namedtuple")
print(p)
print("x:", p.x, "y:", p.y)
print("as dict:", p._asdict())

# 06. OrderedDict - Dict that Remembers Insertion Order
# ------------------------------------
# - Note: regular dicts preserve insertion order since Python 3.7,
#   but OrderedDict offers extra methods like move_to_end().
od = OrderedDict()
od["b"] = 2
od["a"] = 1
od["c"] = 3
print("\n# 06. OrderedDict")
print(od)
od.move_to_end("b")
print("after move_to_end('b'):", od)

# 07. ChainMap - Combine Multiple Dicts into One View
# ------------------------------------
defaults = {"theme": "light", "language": "en"}
overrides = {"theme": "dark"}
combined = ChainMap(overrides, defaults)
print("\n# 07. ChainMap")
print("theme:", combined["theme"])       # overrides wins
print("language:", combined["language"])  # falls back to defaults

# 08. Counter Arithmetic - +, -, &, |
# ------------------------------------
# - Counters support set-like/arithmetic operators. Results drop
#   zero/negative counts (except subtract(), see #09).
stock = Counter(apple=3, banana=1, cherry=0)
sold = Counter(apple=1, banana=2, cherry=5)
print("\n# 08. Counter Arithmetic")
print("stock + sold:", stock + sold)   # add counts
print("stock - sold:", stock - sold)   # subtract, drop <= 0 results
print("stock & sold:", stock & sold)   # min of each count (intersection)
print("stock | sold:", stock | sold)   # max of each count (union)

# 09. Counter.subtract() - In-Place Subtraction (allows negatives)
# ------------------------------------
running_total = Counter(apple=3, banana=1)
running_total.subtract(Counter(apple=1, banana=2))
print("\n# 09. Counter.subtract()")
print(running_total)  # banana goes negative, unlike the '-' operator

# 10. deque(maxlen=N) - Fixed-Size Rolling Buffer
# ------------------------------------
# - Once full, appending drops the oldest item automatically.
# - Useful for "last N events" style tracking (recent logs, undo history).
recent_events = deque(maxlen=3)
print("\n# 10. deque(maxlen=N)")
for event in ["login", "click", "scroll", "logout"]:
    recent_events.append(event)
    print(f"after '{event}':", list(recent_events))

# 11. defaultdict with a Custom Factory Function
# ------------------------------------
# - The factory isn't limited to list/int; any zero-arg callable works.
def new_player():
    return {"score": 0, "lives": 3}

players = defaultdict(new_player)
print("\n# 11. defaultdict with Custom Factory")
players["Alice"]["score"] += 10
players["Bob"]["lives"] -= 1
print(dict(players))

# 12. namedtuple Deeper - _replace(), _fields, Subclassing
# ------------------------------------
print("\n# 12. namedtuple Deeper")
p_moved = p._replace(x=10)          # returns a NEW namedtuple, p is unchanged
print("original p:", p, "| p_moved:", p_moved)
print("field names:", Point._fields)

class Vector(namedtuple("Vector", ["x", "y"])):
    __slots__ = ()  # keep it lightweight, no per-instance __dict__

    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

v = Vector(3, 4)
print("Vector:", v, "| magnitude:", v.magnitude())

# 13. UserDict / UserList / UserString - Subclassing Container-Like Types
# ------------------------------------
# - Subclassing dict/list/str directly can behave oddly (some built-in
#   methods bypass your overrides). UserDict/UserList/UserString wrap a
#   real dict/list/str internally, so overriding methods works reliably.
from collections import UserDict

class TrackedDict(UserDict):
    def __setitem__(self, key, value):
        print(f"  setting {key} = {value}")
        super().__setitem__(key, value)

print("\n# 13. UserDict / UserList / UserString")
td = TrackedDict()
td["a"] = 1
td["b"] = 2
print("final dict:", dict(td))
