import dataclasses
import math

import pytest


@pytest.fixture(scope="module")
def ex(load):
    return load("ex05_oop")


# 1 Rectangle
def test_rectangle_area_perimeter(ex):
    r = ex.Rectangle(3, 4)
    assert r.area() == 12
    assert r.perimeter() == 14
    assert ex.Rectangle(0, 5).area() == 0


def test_rectangle_is_square_and_repr(ex):
    assert ex.Rectangle(2, 2).is_square()
    assert not ex.Rectangle(2, 3).is_square()
    assert repr(ex.Rectangle(3, 4)) == "Rectangle(3, 4)"


def test_rectangle_equality(ex):
    assert ex.Rectangle(3, 4) == ex.Rectangle(3, 4)
    assert ex.Rectangle(3, 4) != ex.Rectangle(4, 3)
    assert (ex.Rectangle(1, 1) == 5) is False


# 2 Temperature
def test_temperature_fahrenheit_read(ex):
    assert ex.Temperature(100).fahrenheit == 212
    assert ex.Temperature().celsius == 0
    assert ex.Temperature(-40).fahrenheit == -40


def test_temperature_fahrenheit_set(ex):
    t = ex.Temperature(50)
    t.fahrenheit = 32
    assert t.celsius == 0
    t.fahrenheit = 212
    assert t.celsius == pytest.approx(100)


def test_temperature_rejects_below_absolute_zero(ex):
    with pytest.raises(ValueError):
        ex.Temperature(-300)
    t = ex.Temperature(10)
    with pytest.raises(ValueError):
        t.celsius = -273.16
    assert t.celsius == 10
    with pytest.raises(ValueError):
        t.fahrenheit = -1000
    assert ex.Temperature(-273.15).celsius == -273.15


# 3 Vector
def test_vector_add_sub(ex):
    v, w = ex.Vector(1, 2), ex.Vector(3, 4)
    assert v + w == ex.Vector(4, 6)
    assert w - v == ex.Vector(2, 2)
    assert -v == ex.Vector(-1, -2)


def test_vector_scalar_multiplication_both_sides(ex):
    v = ex.Vector(1, 2)
    assert v * 3 == ex.Vector(3, 6)
    assert 2 * v == ex.Vector(2, 4)
    assert 0.5 * ex.Vector(2, 2) == ex.Vector(1.0, 1.0)


def test_vector_abs_bool_repr(ex):
    assert abs(ex.Vector(3, 4)) == 5.0
    assert not ex.Vector(0, 0)
    assert ex.Vector(0, 1)
    assert repr(ex.Vector(1, 2)) == "Vector(1, 2)"


def test_vector_bad_operands(ex):
    with pytest.raises(TypeError):
        ex.Vector(1, 2) + 5
    with pytest.raises(TypeError):
        ex.Vector(1, 2) * "a"
    assert ex.Vector(1, 2) != (1, 2)


# 4 BankAccount
def test_account_deposit_withdraw(ex):
    a = ex.BankAccount("Asha", 50)
    assert a.deposit(25) == 75
    assert a.withdraw(30) == 45
    assert a.balance == 45


def test_account_errors(ex):
    a = ex.BankAccount("Asha", 10)
    for bad in (0, -5):
        with pytest.raises(ValueError):
            a.deposit(bad)
        with pytest.raises(ValueError):
            a.withdraw(bad)
    with pytest.raises(ValueError):
        a.withdraw(11)
    assert a.balance == 10
    assert a.withdraw(10) == 0


def test_account_class_attributes_and_count(ex):
    before = ex.BankAccount.count
    ex.BankAccount("A")
    ex.BankAccount("B")
    assert ex.BankAccount.count == before + 2
    assert ex.BankAccount.bank_name == "PyBank"


def test_account_alternative_constructor_and_static(ex):
    a = ex.BankAccount.from_string("Ravi: 10")
    assert (a.owner, a.balance) == ("Ravi", 10)
    assert ex.BankAccount.is_valid_amount(5)
    assert not ex.BankAccount.is_valid_amount(-5)
    assert not ex.BankAccount.is_valid_amount("5")


def test_account_from_string_works_for_subclass(ex):
    class Savings(ex.BankAccount):
        pass

    assert type(Savings.from_string("Z:1")) is Savings


# 5 Employee / Manager
def test_employee_basics(ex):
    e = ex.Employee("Asha", 1200)
    assert e.monthly_pay() == 100
    assert e.describe() == "Asha (Employee)"


def test_manager_pay_and_describe(ex):
    e = ex.Employee("Asha", 1200)
    m = ex.Manager("Ravi", 2400)
    assert m.monthly_pay() == 200
    m.add_report(e)
    m.add_report(ex.Employee("Bo", 1))
    assert m.monthly_pay() == 400
    assert m.describe() == "Ravi (Manager)"
    assert isinstance(m, ex.Employee)


def test_manager_reports_not_shared(ex):
    a, b = ex.Manager("A", 12), ex.Manager("B", 12)
    a.add_report(ex.Employee("x", 1))
    assert b.reports == []
    given = [ex.Employee("y", 1)]
    c = ex.Manager("C", 12, given)
    c.add_report(ex.Employee("z", 1))
    assert len(given) == 1


# 6 Shapes (ABC)
def test_shape_is_abstract(ex):
    with pytest.raises(TypeError):
        ex.Shape()

    class Bad(ex.Shape):
        pass

    with pytest.raises(TypeError):
        Bad()


def test_shapes_area(ex):
    assert ex.Circle(1).area() == pytest.approx(math.pi)
    assert ex.Square(3).area() == 9
    assert isinstance(ex.Circle(1), ex.Shape)


def test_shape_describe_and_total(ex):
    assert ex.Circle(1).describe() == "Circle with area 3.14"
    assert ex.Square(2).describe() == "Square with area 4.00"
    assert ex.total_area([ex.Square(2), ex.Square(3)]) == 13
    assert ex.total_area([]) == 0


# 7 dataclasses
def test_item_total_and_defaults(ex):
    i = ex.Item(2.5, "pen", 4)
    assert i.total == 10.0
    assert ex.Item(1, "a").qty == 1
    assert dataclasses.is_dataclass(ex.Item)


def test_item_is_frozen_and_equal(ex):
    i = ex.Item(1, "a")
    with pytest.raises(dataclasses.FrozenInstanceError):
        i.qty = 3
    assert ex.Item(1, "a") == ex.Item(1, "a")


def test_item_ordering(ex):
    assert ex.Item(1, "z") < ex.Item(2, "a")
    assert sorted([ex.Item(3, "c"), ex.Item(1, "a")])[0].name == "a"


def test_cart_default_list_not_shared(ex):
    a, b = ex.Cart(), ex.Cart()
    a.add(ex.Item(1, "x"))
    assert b.items == []
    assert dataclasses.is_dataclass(ex.Cart)


def test_cart_total(ex):
    c = ex.Cart()
    assert c.total() == 0
    c.add(ex.Item(2, "a", 3))
    c.add(ex.Item(1, "b"))
    assert c.total() == 7


# 8 Playlist
def test_playlist_len_and_index(ex):
    p = ex.Playlist("a", "b", "c")
    assert len(p) == 3
    assert p[0] == "a" and p[-1] == "c"
    assert p[0:2] == ["a", "b"]


def test_playlist_iteration_contains(ex):
    p = ex.Playlist("a", "b")
    assert list(p) == ["a", "b"]
    assert list(p) == ["a", "b"]  # can loop twice
    assert "a" in p and "z" not in p
    assert list(reversed(p)) == ["b", "a"]


def test_playlist_add_empty_repr(ex):
    p = ex.Playlist()
    assert len(p) == 0 and list(p) == []
    p.add("x")
    assert repr(p) == "Playlist('x')"
    with pytest.raises(IndexError):
        p[5]


# 9 Countdown
def test_countdown_values(ex):
    assert list(ex.Countdown(3)) == [3, 2, 1]
    assert list(ex.Countdown(1)) == [1]


def test_countdown_empty(ex):
    assert list(ex.Countdown(0)) == []
    assert list(ex.Countdown(-2)) == []


def test_countdown_is_used_up(ex):
    c = ex.Countdown(2)
    assert iter(c) is c
    assert list(c) == [2, 1]
    assert list(c) == []
    with pytest.raises(StopIteration):
        next(c)


# 10 composition
def test_engine_start_stop(ex):
    e = ex.Engine(90)
    assert e.running is False
    assert e.start() is True
    assert e.start() is False
    e.stop()
    assert e.running is False


def test_car_uses_engine(ex):
    car = ex.Car("Mini", ex.Engine(90))
    assert not car.is_running
    assert car.start() == "Mini started"
    assert car.start() == "Mini already running"
    assert car.is_running
    car.stop()
    assert not car.is_running


def test_car_accepts_any_engine_like_object(ex):
    class Fake:
        running = False

        def start(self):
            self.running = True
            return True

        def stop(self):
            self.running = False

    car = ex.Car("Toy", Fake())
    assert car.start() == "Toy started"
    assert car.is_running


# 11 strategy
def test_discount_strategies(ex):
    assert ex.no_discount(100) == 100
    assert ex.percent_off(10)(200) == 180
    assert ex.percent_off(0)(50) == 50
    assert ex.flat_off(50)(200) == 150


def test_flat_off_never_negative(ex):
    assert ex.flat_off(50)(30) == 0
    assert ex.flat_off(0)(5) == 5


def test_checkout_and_swapping_strategy(ex):
    c = ex.Checkout([100, 100])
    assert c.total() == 200
    c.set_strategy(ex.percent_off(50))
    assert c.total() == 100
    assert ex.Checkout([], ex.flat_off(5)).total() == 0
    assert ex.Checkout([10], strategy=lambda s: s + 1).total() == 11


# 12 observer
def test_emitter_calls_in_order(ex):
    e, seen = ex.EventEmitter(), []
    e.on("hi", lambda x: seen.append(("a", x)))
    e.on("hi", lambda x: seen.append(("b", x)))
    assert e.emit("hi", 1) == 2
    assert seen == [("a", 1), ("b", 1)]


def test_emitter_unknown_event_and_kwargs(ex):
    e, seen = ex.EventEmitter(), []
    assert e.emit("nothing") == 0
    e.on("x", lambda *a, **k: seen.append((a, k)))
    e.emit("x", 1, 2, key="v")
    assert seen == [((1, 2), {"key": "v"})]


def test_emitter_off_and_on_returns_callback(ex):
    e, seen = ex.EventEmitter(), []

    def handler():
        seen.append(1)

    assert e.on("ping", handler) is handler
    e.emit("ping")
    e.off("ping", handler)
    e.off("ping", handler)  # unknown now: no error
    e.off("never", handler)
    assert e.emit("ping") == 0
    assert seen == [1]


def test_emitter_callback_can_remove_itself(ex):
    e, seen = ex.EventEmitter(), []

    def once():
        seen.append("once")
        e.off("go", once)

    e.on("go", once)
    e.on("go", lambda: seen.append("other"))
    e.emit("go")
    e.emit("go")
    assert seen == ["once", "other", "other"]


def test_emitter_counts_callbacks_that_remove_themselves(ex):
    emitter = ex.EventEmitter()
    def once():
        emitter.off("event", once)
    emitter.on("event", once)
    assert emitter.emit("event") == 1
    assert emitter.emit("event") == 0
