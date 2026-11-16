import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex04_functions_and_functional")


def test_greet_defaults(ex):
    assert ex.greet("Asha") == "Hello Asha!"
    assert ex.greet("Asha", "Hi") == "Hi Asha!"
    assert ex.greet("Asha", "Hi", punctuation=".") == "Hi Asha."


def test_greet_punctuation_is_keyword_only(ex):
    assert ex.greet("Bo", punctuation="") == "Hello Bo"
    with pytest.raises(TypeError):
        ex.greet("Bo", "Hi", "?")


def test_build_url_parts(ex):
    assert ex.build_url("http://x.com", "api", "users") == "http://x.com/api/users"
    assert ex.build_url("http://x.com") == "http://x.com"


def test_build_url_params_and_slashes(ex):
    assert ex.build_url("http://x.com/", "/api/", page=2, q="a") == "http://x.com/api?page=2&q=a"
    assert ex.build_url("http://x.com", id=7) == "http://x.com?id=7"


def test_append_item_new_list_each_call(ex):
    assert ex.append_item(1) == [1]
    assert ex.append_item(2) == [2]
    assert ex.append_item(3) == [3]


def test_append_item_does_not_change_input(ex):
    a = [1]
    assert ex.append_item(2, a) == [1, 2]
    assert a == [1]
    assert ex.append_item(1, []) == [1]


def test_make_counter_default(ex):
    c = ex.make_counter()
    assert [c(), c(), c()] == [0, 1, 2]


def test_make_counter_start_step(ex):
    c = ex.make_counter(5, 2)
    assert [c(), c(), c()] == [5, 7, 9]
    assert ex.make_counter(step=-1, start=0)() == 0


def test_make_counter_independent(ex):
    a, b = ex.make_counter(), ex.make_counter(100)
    a(); a()
    assert b() == 100
    assert a() == 2


def test_make_multiplier(ex):
    double = ex.make_multiplier(2)
    assert double(21) == 42
    assert ex.make_multiplier(0)(99) == 0
    assert ex.make_multiplier(3)("ab") == "ababab"


def test_make_multiplier_in_loop_keeps_own_n(ex):
    funcs = [ex.make_multiplier(i) for i in range(1, 4)]
    assert [f(10) for f in funcs] == [10, 20, 30]


def test_flatten_basic(ex):
    assert ex.flatten([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]
    assert ex.flatten([]) == []
    assert ex.flatten([[], [[]]]) == []


def test_flatten_keeps_strings_whole(ex):
    assert ex.flatten(["ab", ["c", ("de",)]]) == ["ab", "c", "de"]


def test_flatten_deep(ex):
    deep = [1]
    for _ in range(50):
        deep = [deep]
    assert ex.flatten(deep) == [1]


def test_clean_names_drops_blank_and_sorts(ex):
    assert ex.clean_names(["  zed ", "", "amy", "   ", "BOB"]) == ["Amy", "Bob", "Zed"]


def test_clean_names_length_then_alpha(ex):
    assert ex.clean_names(["mia", "al", "joe"]) == ["Al", "Joe", "Mia"]
    assert ex.clean_names(["christopher", "ed"]) == ["Ed", "Christopher"]
    assert ex.clean_names([]) == []


def test_merge_dicts_later_wins(ex):
    assert ex.merge_dicts([{"a": 1}, {"b": 2}, {"a": 3}]) == {"a": 3, "b": 2}


def test_merge_dicts_empty_and_single(ex):
    assert ex.merge_dicts([]) == {}
    assert ex.merge_dicts([{"a": 1}]) == {"a": 1}


def test_merge_dicts_does_not_mutate(ex):
    first, second = {"a": 1}, {"b": 2}
    ex.merge_dicts([first, second])
    assert first == {"a": 1} and second == {"b": 2}


def test_make_power(ex):
    assert ex.make_power(2)(7) == 49
    assert ex.make_power(3)(2) == 8
    assert ex.make_power(0)(99) == 1


def test_make_power_is_partial(ex):
    import functools
    assert isinstance(ex.make_power(2), functools.partial)


def test_compose_order_left_to_right(ex):
    assert ex.compose(str.strip, str.upper)("  hi ") == "HI"
    assert ex.compose(lambda x: x + 1, lambda x: x * 2)(3) == 8
    assert ex.compose(lambda x: x * 2, lambda x: x + 1)(3) == 7


def test_compose_empty_and_single(ex):
    assert ex.compose()(5) == 5
    assert ex.compose(len)("abc") == 3


def test_memoize_runs_once_per_args(ex):
    calls = []

    @ex.memoize
    def sq(x):
        calls.append(x)
        return x * x

    assert sq(4) == 16 and sq(4) == 16
    assert sq(5) == 25
    assert calls == [4, 5]


def test_memoize_kwargs_and_name(ex):
    calls = []

    @ex.memoize
    def add(a, b=0):
        calls.append((a, b))
        return a + b

    assert add(1, b=2) == 3 and add(1, b=2) == 3
    assert add(1) == 1
    assert len(calls) == 2
    assert add.__name__ == "add"


def test_memoize_makes_recursive_fib_fast(ex):
    @ex.memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(80) == 23416728348467685


def test_count_calls_counts(ex):
    @ex.count_calls
    def f(x):
        return x + 1

    assert f.calls == 0
    assert f(1) == 2 and f(2) == 3
    assert f.calls == 2


def test_count_calls_keeps_metadata(ex):
    @ex.count_calls
    def f():
        "doc here"

    assert f.__name__ == "f"
    assert f.__doc__ == "doc here"


def test_count_calls_counts_failures(ex):
    @ex.count_calls
    def boom():
        raise ValueError

    for _ in range(2):
        with pytest.raises(ValueError):
            boom()
    assert boom.calls == 2
