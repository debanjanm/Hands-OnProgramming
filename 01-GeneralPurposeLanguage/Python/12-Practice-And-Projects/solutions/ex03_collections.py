"""Exercise set 3: lists, tuples, sets, dicts, comprehensions and sorting."""


def unique_preserve_order(items):
    """Level: easy
    Remove duplicates from a list but keep the order of first appearance.
    Items are hashable. Return a new list.
    Example: unique_preserve_order([3, 1, 3, 2, 1]) -> [3, 1, 2]
    Hint: dict.fromkeys(items) keeps insertion order; or use a "seen" set.
    """
    return list(dict.fromkeys(items))


def second_largest(nums):
    """Level: easy
    Return the second largest DISTINCT value, or None if there are fewer than 2 distinct values.
    Example: second_largest([5, 9, 9, 2]) -> 5, second_largest([4, 4]) -> None
    Hint: sorted(set(nums)) then take [-2].
    """
    distinct = sorted(set(nums))
    return distinct[-2] if len(distinct) >= 2 else None


def common_and_unique(a, b):
    """Level: easy
    Given two lists, return a tuple of three sorted lists:
    (in both, only in a, only in b). Duplicates are ignored.
    Example: common_and_unique([1, 2, 3], [2, 3, 4]) -> ([2, 3], [1], [4])
    Hint: set operations & and -.
    """
    sa, sb = set(a), set(b)
    return sorted(sa & sb), sorted(sa - sb), sorted(sb - sa)


def group_by_length(words):
    """Level: medium
    Group words by their length. Return a dict {length: [words...]} where each
    list keeps the original order.
    Example: group_by_length(["hi", "yo", "cat"]) -> {2: ["hi", "yo"], 3: ["cat"]}
    Hint: dict.setdefault(length, []).append(word), or collections.defaultdict(list).
    """
    groups = {}
    for w in words:
        groups.setdefault(len(w), []).append(w)
    return groups


def invert_dict(d):
    """Level: medium
    Swap keys and values. Because values can repeat, each new value is a list of
    the old keys (in the original order).
    Example: invert_dict({"a": 1, "b": 2, "c": 1}) -> {1: ["a", "c"], 2: ["b"]}
    Hint: loop over d.items() and use setdefault.
    """
    out = {}
    for k, v in d.items():
        out.setdefault(v, []).append(k)
    return out


def sort_people(people):
    """Level: medium
    people is a list of dicts with "name" and "age". Return a NEW list sorted by
    age descending, then by name ascending (case-insensitive). Do not change the input.
    Example: sort_people([{"name": "Bo", "age": 30}, {"name": "Al", "age": 30}, {"name": "Cy", "age": 40}])
             -> Cy (40), Al (30), Bo (30)
    Hint: sorted(..., key=lambda p: (-p["age"], p["name"].lower())).
    """
    return sorted(people, key=lambda p: (-p["age"], p["name"].lower()))


def merge_dicts_sum(a, b):
    """Level: medium
    Merge two dicts of numbers. Keys in both get their values added. Return a new
    dict and leave the inputs unchanged.
    Example: merge_dicts_sum({"x": 1, "y": 2}, {"y": 5, "z": 1}) -> {"x": 1, "y": 7, "z": 1}
    Hint: start with dict(a), then loop over b with .get(key, 0).
    """
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + v
    return out


def rotate_list(items, k):
    """Level: medium
    Rotate a list to the right by k places and return a new list. k may be larger
    than the length or negative (negative rotates left). Empty list -> [].
    Example: rotate_list([1, 2, 3, 4, 5], 2) -> [4, 5, 1, 2, 3], rotate_list([1, 2, 3], -1) -> [2, 3, 1]
    Hint: k %= len(items) then slice: items[-k:] + items[:-k] (careful when k is 0).
    """
    if not items:
        return []
    k %= len(items)
    return items[len(items) - k:] + items[:len(items) - k]


def top_n_frequent(items, n):
    """Level: medium
    Return the n most frequent items as a list of (item, count) tuples, highest
    count first. Ties keep first-appearance order.
    Example: top_n_frequent(["a", "b", "b", "c", "c", "a", "d"], 2) -> [("a", 2), ("b", 2)]
    Hint: collections.Counter(...).most_common(n) already breaks ties by first seen.
    """
    from collections import Counter
    return Counter(items).most_common(n)


def transpose(matrix):
    """Level: medium
    Transpose a rectangular matrix (list of rows) so rows become columns.
    Return a list of lists. An empty matrix gives [].
    Example: transpose([[1, 2, 3], [4, 5, 6]]) -> [[1, 4], [2, 5], [3, 6]]
    Hint: zip(*matrix) with a list comprehension to turn tuples into lists.
    """
    return [list(col) for col in zip(*matrix)]


def matrix_multiply(a, b):
    """Level: hard
    Multiply matrix a (m x n) by matrix b (n x p) and return the m x p result.
    Raise ValueError if the inner sizes do not match.
    Example: matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]]) -> [[19, 22], [43, 50]]
    Hint: cell [i][j] = sum(a[i][k] * b[k][j]); transpose b to loop over its columns.
    """
    if len(a[0]) != len(b):
        raise ValueError("inner dimensions do not match")
    cols = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in cols] for row in a]


def flatten(nested):
    """Level: hard
    Flatten lists nested to any depth into one flat list, keeping order. Only
    lists are unpacked (strings and tuples are kept whole).
    Example: flatten([1, [2, [3, 4]], [], [[5]]]) -> [1, 2, 3, 4, 5]
    Hint: recursion: if an item is a list, extend with flatten(item), else append.
    """
    out = []
    for item in nested:
        if isinstance(item, list):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out
