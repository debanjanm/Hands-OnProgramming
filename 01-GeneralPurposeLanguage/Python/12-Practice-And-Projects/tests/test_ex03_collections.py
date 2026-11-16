import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex03_collections")


def test_unique_preserve_order(ex):
    assert ex.unique_preserve_order([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert ex.unique_preserve_order([]) == []
    assert ex.unique_preserve_order("hello") == ["h", "e", "l", "o"]


def test_unique_returns_new_list(ex):
    data = [1, 1, 2]
    result = ex.unique_preserve_order(data)
    assert data == [1, 1, 2]
    assert result is not data


def test_second_largest(ex):
    assert ex.second_largest([5, 9, 9, 2]) == 5
    assert ex.second_largest([4, 4]) is None
    assert ex.second_largest([]) is None
    assert ex.second_largest([-1, -5, -3]) == -3


def test_common_and_unique(ex):
    assert ex.common_and_unique([1, 2, 3], [2, 3, 4]) == ([2, 3], [1], [4])
    assert ex.common_and_unique([], [1]) == ([], [], [1])
    assert ex.common_and_unique([1, 1, 2], [2, 2]) == ([2], [1], [])


def test_group_by_length(ex):
    assert ex.group_by_length(["hi", "yo", "cat"]) == {2: ["hi", "yo"], 3: ["cat"]}
    assert ex.group_by_length([]) == {}
    assert ex.group_by_length(["", "a", ""]) == {0: ["", ""], 1: ["a"]}


def test_invert_dict(ex):
    assert ex.invert_dict({"a": 1, "b": 2, "c": 1}) == {1: ["a", "c"], 2: ["b"]}
    assert ex.invert_dict({}) == {}
    assert ex.invert_dict({"x": "y"}) == {"y": ["x"]}


def test_sort_people(ex):
    people = [{"name": "Bo", "age": 30}, {"name": "Al", "age": 30}, {"name": "Cy", "age": 40}]
    result = ex.sort_people(people)
    assert [p["name"] for p in result] == ["Cy", "Al", "Bo"]
    assert [p["name"] for p in people] == ["Bo", "Al", "Cy"]  # input untouched


def test_sort_people_case_insensitive_and_empty(ex):
    people = [{"name": "bob", "age": 20}, {"name": "Alice", "age": 20}]
    assert [p["name"] for p in ex.sort_people(people)] == ["Alice", "bob"]
    assert ex.sort_people([]) == []


def test_merge_dicts_sum(ex):
    a, b = {"x": 1, "y": 2}, {"y": 5, "z": 1}
    assert ex.merge_dicts_sum(a, b) == {"x": 1, "y": 7, "z": 1}
    assert a == {"x": 1, "y": 2} and b == {"y": 5, "z": 1}
    assert ex.merge_dicts_sum({}, {}) == {}
    assert ex.merge_dicts_sum({"a": 1.5}, {}) == {"a": 1.5}


def test_rotate_list(ex):
    assert ex.rotate_list([1, 2, 3, 4, 5], 2) == [4, 5, 1, 2, 3]
    assert ex.rotate_list([1, 2, 3], -1) == [2, 3, 1]
    assert ex.rotate_list([1, 2, 3], 0) == [1, 2, 3]
    assert ex.rotate_list([1, 2, 3], 7) == [3, 1, 2]
    assert ex.rotate_list([], 3) == []


def test_top_n_frequent(ex):
    data = ["a", "b", "b", "c", "c", "a", "d"]
    assert ex.top_n_frequent(data, 2) == [("a", 2), ("b", 2)]
    assert ex.top_n_frequent("mississippi", 1) == [("i", 4)]
    assert ex.top_n_frequent([], 3) == []
    assert ex.top_n_frequent([1, 2], 5) == [(1, 1), (2, 1)]


def test_transpose(ex):
    assert ex.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert ex.transpose([[7]]) == [[7]]
    assert ex.transpose([]) == []
    assert ex.transpose([[1, 2, 3]]) == [[1], [2], [3]]


def test_matrix_multiply(ex):
    assert ex.matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]]) == [[19, 22], [43, 50]]
    assert ex.matrix_multiply([[1, 2, 3]], [[1], [2], [3]]) == [[14]]
    identity = [[1, 0], [0, 1]]
    assert ex.matrix_multiply([[4, 5], [6, 7]], identity) == [[4, 5], [6, 7]]


def test_matrix_multiply_bad_shapes(ex):
    with pytest.raises(ValueError):
        ex.matrix_multiply([[1, 2]], [[1, 2]])


def test_flatten(ex):
    assert ex.flatten([1, [2, [3, 4]], [], [[5]]]) == [1, 2, 3, 4, 5]
    assert ex.flatten([]) == []
    assert ex.flatten([["a", "bc"], ("t", 1)]) == ["a", "bc", ("t", 1)]
    assert ex.flatten([[[[]]]]) == []
