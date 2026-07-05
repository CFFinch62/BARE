"""Integration tests for BARE error reporting.

Verifies that parse-time and runtime errors produce the spec's
single-line diagnostic format:  Error on line N: message
"""

import pytest
from bare_core.lexer import Lexer
from bare_core.parser import Parser
from bare_core.interpreter import Interpreter
from bare_core.errors import BareError, BareLexerError, BareParseError, BareRuntimeError


class TestErrorFormat:
    """All errors should produce 'Error on line N: message' format."""

    def test_lexer_error_format(self):
        with pytest.raises(BareLexerError) as exc_info:
            Lexer('"unterminated').tokenize()
        msg = exc_info.value.format()
        assert msg.startswith("Error on line 1:")

    def test_parse_error_format(self):
        with pytest.raises(BareParseError) as exc_info:
            tokens = Lexer("if true\n  print 1").tokenize()
            Parser(tokens).parse()
        msg = exc_info.value.format()
        assert "Error on line" in msg

    def test_runtime_error_format(self):
        with pytest.raises(BareRuntimeError) as exc_info:
            tokens = Lexer("print x").tokenize()
            program = Parser(tokens).parse()
            Interpreter().execute(program)
        msg = exc_info.value.format()
        assert msg.startswith("Error on line 1:")
        assert "not defined" in msg


class TestRuntimeErrors:
    def test_undefined_variable_error(self, run):
        with pytest.raises(BareRuntimeError) as exc_info:
            run("print unknown_var")
        assert "not defined" in exc_info.value.message

    def test_type_error_arithmetic(self, run):
        with pytest.raises(BareRuntimeError):
            run('print "hello" - 1')

    def test_index_out_of_range(self, run):
        with pytest.raises(BareRuntimeError, match="out of range"):
            run("x = [1, 2]\nprint x[5]")

    def test_division_by_zero(self, run):
        with pytest.raises(BareRuntimeError, match="division by zero"):
            run("print 1 / 0")

    def test_cannot_negate_string(self, run):
        with pytest.raises(BareRuntimeError, match="cannot negate"):
            run('print -"hello"')

    def test_index_into_non_list(self, run):
        with pytest.raises(BareRuntimeError, match="cannot index"):
            run("x = 5\nprint x[0]")

    def test_call_undefined_function(self, run):
        with pytest.raises(BareRuntimeError, match="not defined"):
            run("ghost()")

    def test_wrong_arg_count(self, run):
        with pytest.raises(BareRuntimeError, match="expects"):
            run("sub f(a)\n  return a\nend\nf(1, 2)")

    def test_num_conversion_error(self, run):
        with pytest.raises(BareRuntimeError, match="cannot convert"):
            run('print num("not_a_number")')

    def test_error_line_number(self):
        """Error should report the correct line number."""
        source = "x = 1\ny = 2\nprint z"
        with pytest.raises(BareRuntimeError) as exc_info:
            tokens = Lexer(source).tokenize()
            program = Parser(tokens).parse()
            Interpreter().execute(program)
        assert exc_info.value.location.line == 3


class TestParseErrors:
    def test_missing_end_for_if(self):
        with pytest.raises(BareParseError, match="expected 'end'"):
            tokens = Lexer("if true\n  print 1").tokenize()
            Parser(tokens).parse()

    def test_missing_end_for_while(self):
        with pytest.raises(BareParseError, match="expected 'end'"):
            tokens = Lexer("while true\n  print 1").tokenize()
            Parser(tokens).parse()

    def test_missing_end_for_sub(self):
        with pytest.raises(BareParseError, match="expected 'end'"):
            tokens = Lexer("sub f()\n  print 1").tokenize()
            Parser(tokens).parse()
