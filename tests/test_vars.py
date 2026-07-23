"""Tests for Variable, StringVar, IntVar, DoubleVar, BooleanVar."""

from unittest.mock import MagicMock

from iskg.vars import BooleanVar, DoubleVar, IntVar, StringVar, Variable


class TestVariable:
    def test_default_value_is_none(self):
        v = Variable()
        assert v.get() is None

    def test_init_with_value(self):
        v = Variable(42)
        assert v.get() == 42

    def test_set_and_get(self):
        v = Variable()
        v.set("hello")
        assert v.get() == "hello"

    def test_set_overwrites(self):
        v = Variable(1)
        v.set(2)
        assert v.get() == 2

    def test_trace_write_called_on_set(self):
        v = Variable()
        calls = []
        v.trace_add("write", lambda *a: calls.append(a))
        v.set("x")
        assert len(calls) == 1
        assert calls[0][2] == "write"

    def test_trace_read_not_called_on_set(self):
        v = Variable()
        calls = []
        v.trace_add("read", lambda *a: calls.append(a))
        v.set("x")
        assert len(calls) == 0

    def test_trace_remove(self):
        v = Variable()
        calls = []

        def cb(*a):
            return calls.append(1)

        v.trace_add("write", cb)
        v.trace_remove("write", cb)
        v.set("x")
        assert calls == []

    def test_trace_remove_partial(self):
        v = Variable()
        calls = []

        def cb1(*a):
            return calls.append(1)

        def cb2(*a):
            return calls.append(2)

        v.trace_add("write", cb1)
        v.trace_add("write", cb2)
        v.trace_remove("write", cb1)
        v.set("x")
        assert calls == [2]

    def test_widget_notified_on_set(self):
        v = Variable()
        w = MagicMock()
        v._widgets.append(w)
        v.set("val")
        w._var_updated.assert_called_once_with(v)

    def test_from_widget_suppresses_echo(self):
        v = Variable()
        w = MagicMock()
        w2 = MagicMock()
        v._widgets.append(w)
        v._widgets.append(w2)
        v.set("val", _from_widget=w)
        w._var_updated.assert_not_called()
        w2._var_updated.assert_called_once_with(v)

    def test_get_after_none(self):
        v = Variable()
        v.set(None)
        assert v.get() is None


class TestStringVar:
    def test_default_empty_string(self):
        v = StringVar()
        assert v.get() == ""

    def test_init_with_value(self):
        v = StringVar("hello")
        assert v.get() == "hello"

    def test_set_coerces_to_str(self):
        v = StringVar()
        v.set(42)
        assert v.get() == "42"
        assert isinstance(v.get(), str)

    def test_get_returns_empty_string_on_none(self):
        v = StringVar()
        v._value = None
        assert v.get() == ""


class TestIntVar:
    def test_default_zero(self):
        v = IntVar()
        assert v.get() == 0

    def test_init_with_value(self):
        v = IntVar(10)
        assert v.get() == 10

    def test_set_coerces_to_int(self):
        v = IntVar()
        v.set("42")
        assert v.get() == 42
        assert isinstance(v.get(), int)

    def test_set_float_truncates(self):
        v = IntVar()
        v.set(3.9)
        assert v.get() == 3

    def test_get_returns_zero_on_none(self):
        v = IntVar()
        v._value = None
        assert v.get() == 0


class TestDoubleVar:
    def test_default_zero(self):
        v = DoubleVar()
        assert v.get() == 0.0

    def test_init_with_value(self):
        v = DoubleVar(3.14)
        assert v.get() == 3.14

    def test_set_coerces_to_float(self):
        v = DoubleVar()
        v.set("2.5")
        assert v.get() == 2.5
        assert isinstance(v.get(), float)

    def test_set_int_becomes_float(self):
        v = DoubleVar()
        v.set(42)
        assert v.get() == 42.0

    def test_get_returns_zero_on_none(self):
        v = DoubleVar()
        v._value = None
        assert v.get() == 0.0


class TestBooleanVar:
    def test_default_false(self):
        v = BooleanVar()
        assert v.get() is False

    def test_init_true(self):
        v = BooleanVar(True)
        assert v.get() is True

    def test_set_true(self):
        v = BooleanVar()
        v.set(True)
        assert v.get() is True

    def test_set_false(self):
        v = BooleanVar()
        v.set(False)
        assert v.get() is False

    def test_set_string_true(self):
        v = BooleanVar()
        v.set("true")
        assert v.get() is True

    def test_set_string_false(self):
        v = BooleanVar()
        v.set("false")
        assert v.get() is False

    def test_set_truthy_int(self):
        v = BooleanVar()
        v.set(1)
        assert v.get() is True

    def test_set_falsy_int(self):
        v = BooleanVar()
        v.set(0)
        assert v.get() is False

    def test_get_returns_false_on_none(self):
        v = BooleanVar()
        v._value = None
        assert v.get() is False
