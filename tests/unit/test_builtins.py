"""Unit tests for BARE built-in functions."""

import pytest
from bare_core.errors import BareRuntimeError


class TestLen:
    def test_string_length(self, run):
        assert run('print len("hello")') == ["5"]

    def test_empty_string_length(self, run):
        assert run('print len("")') == ["0"]

    def test_list_length(self, run):
        assert run("print len([1, 2, 3])") == ["3"]

    def test_empty_list_length(self, run):
        assert run("print len([])") == ["0"]

    def test_wrong_type(self, run):
        with pytest.raises(BareRuntimeError, match="string or list"):
            run("print len(42)")

    def test_wrong_arg_count(self, run):
        with pytest.raises(BareRuntimeError, match="expects 1"):
            run("print len(1, 2)")


class TestAppend:
    def test_append_to_list(self, run):
        assert run("x = [1, 2]\nappend(x, 3)\nprint x") == ["[1, 2, 3]"]

    def test_append_returns_list(self, run):
        assert run("x = [1]\nprint append(x, 2)") == ["[1, 2]"]

    def test_append_non_list(self, run):
        with pytest.raises(BareRuntimeError, match="expects a list"):
            run('append("hello", 1)')


class TestStr:
    def test_number_to_string(self, run):
        assert run('print str(42)') == ["42"]

    def test_bool_to_string(self, run):
        assert run('print str(true)') == ["true"]

    def test_null_to_string(self, run):
        assert run('print str(null)') == ["null"]

    def test_list_to_string(self, run):
        assert run('print str([1, 2])') == ["[1, 2]"]


class TestNum:
    def test_string_to_number(self, run):
        assert run('print num("42")') == ["42"]

    def test_decimal_string(self, run):
        assert run('print num("3.14")') == ["3.14"]

    def test_already_number(self, run):
        assert run("print num(42)") == ["42"]

    def test_invalid_string(self, run):
        with pytest.raises(BareRuntimeError, match="cannot convert"):
            run('print num("abc")')


class TestRandom:
    def test_random_in_range(self, run):
        """random(1, 1) should always return 1."""
        assert run("print random(1, 1)") == ["1"]

    def test_random_min_max(self, run):
        with pytest.raises(BareRuntimeError, match="must be <="):
            run("print random(10, 1)")

    def test_random_non_number(self, run):
        with pytest.raises(BareRuntimeError, match="expects two numbers"):
            run('print random("a", "b")')


class TestRound:
    def test_round_down(self, run):
        assert run("print round(3.14159, 2)") == ["3.14"]

    def test_round_half_up(self, run):
        """2.5 rounds to 3, not 2 — students expect math-class rounding,
        not Python's default banker's rounding."""
        assert run("print round(2.5, 0)") == ["3"]

    def test_round_negative_half_up(self, run):
        assert run("print round(-2.5, 0)") == ["-3"]

    def test_round_to_zero_places(self, run):
        assert run("print round(4.7, 0)") == ["5"]

    def test_round_already_exact(self, run):
        assert run("print round(2, 2)") == ["2"]

    def test_round_non_number(self, run):
        with pytest.raises(BareRuntimeError, match="expects a number"):
            run('print round("a", 2)')

    def test_round_negative_decimals(self, run):
        with pytest.raises(BareRuntimeError, match="non-negative whole number"):
            run("print round(3.14, -1)")

    def test_round_fractional_decimals(self, run):
        with pytest.raises(BareRuntimeError, match="non-negative whole number"):
            run("print round(3.14, 1.5)")

    def test_round_wrong_arg_count(self, run):
        with pytest.raises(BareRuntimeError, match="expects 2"):
            run("print round(3.14)")


class TestInput:
    def test_input_returns_string(self, run):
        result = run('x = input("name: ")\nprint x', input_values=["Alice"])
        assert result == ["Alice"]

    def test_input_no_prompt(self, run):
        result = run('x = input()\nprint x', input_values=["test"])
        assert result == ["test"]
