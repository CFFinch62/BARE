"""Unit tests for the BARE parser."""

import pytest
from bare_core.lexer import Lexer
from bare_core.parser import Parser
from bare_core.ast_nodes import (
    Assignment,
    BinaryOp,
    BooleanLiteral,
    CallStatement,
    FunctionCall,
    Identifier,
    IfStatement,
    IndexAccess,
    IndexAssignment,
    ListLiteral,
    NullLiteral,
    NumberLiteral,
    PrintStatement,
    Program,
    ReturnStatement,
    StringLiteral,
    SubDefinition,
    UnaryOp,
    WhileStatement,
)
from bare_core.errors import BareParseError


class TestAssignment:
    def test_simple_assignment(self, parse):
        prog = parse("x = 5")
        assert len(prog.statements) == 1
        stmt = prog.statements[0]
        assert isinstance(stmt, Assignment)
        assert stmt.name == "x"
        assert isinstance(stmt.value, NumberLiteral)
        assert stmt.value.value == 5.0

    def test_string_assignment(self, parse):
        prog = parse('name = "hello"')
        stmt = prog.statements[0]
        assert isinstance(stmt.value, StringLiteral)
        assert stmt.value.value == "hello"

    def test_expression_assignment(self, parse):
        prog = parse("x = 1 + 2")
        stmt = prog.statements[0]
        assert isinstance(stmt.value, BinaryOp)


class TestPrint:
    def test_print_number(self, parse):
        prog = parse("print 42")
        stmt = prog.statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expression, NumberLiteral)

    def test_print_string(self, parse):
        prog = parse('print "hello"')
        stmt = prog.statements[0]
        assert isinstance(stmt.expression, StringLiteral)

    def test_print_expression(self, parse):
        prog = parse("print 1 + 2")
        stmt = prog.statements[0]
        assert isinstance(stmt.expression, BinaryOp)


class TestIfStatement:
    def test_simple_if(self, parse):
        prog = parse("if true\n  print 1\nend")
        stmt = prog.statements[0]
        assert isinstance(stmt, IfStatement)
        assert isinstance(stmt.condition, BooleanLiteral)
        assert len(stmt.body) == 1
        assert len(stmt.else_body) == 0

    def test_if_else(self, parse):
        prog = parse("if x == 1\n  print 1\nelse\n  print 2\nend")
        stmt = prog.statements[0]
        assert isinstance(stmt, IfStatement)
        assert len(stmt.body) == 1
        assert len(stmt.else_body) == 1

    def test_nested_if(self, parse):
        source = "if true\n  if false\n    print 1\n  end\nend"
        prog = parse(source)
        outer = prog.statements[0]
        assert isinstance(outer, IfStatement)
        inner = outer.body[0]
        assert isinstance(inner, IfStatement)


class TestWhileStatement:
    def test_simple_while(self, parse):
        prog = parse("while true\n  print 1\nend")
        stmt = prog.statements[0]
        assert isinstance(stmt, WhileStatement)
        assert isinstance(stmt.condition, BooleanLiteral)
        assert len(stmt.body) == 1


class TestSubDefinition:
    def test_no_params(self, parse):
        prog = parse("sub greet()\n  print \"hi\"\nend")
        stmt = prog.statements[0]
        assert isinstance(stmt, SubDefinition)
        assert stmt.name == "greet"
        assert stmt.params == []

    def test_with_params(self, parse):
        prog = parse("sub add(a, b)\n  return a + b\nend")
        stmt = prog.statements[0]
        assert isinstance(stmt, SubDefinition)
        assert stmt.params == ["a", "b"]
        assert len(stmt.body) == 1

    def test_no_body(self, parse):
        prog = parse("sub empty()\nend")
        stmt = prog.statements[0]
        assert isinstance(stmt, SubDefinition)
        assert len(stmt.body) == 0


class TestReturn:
    def test_return_value(self, parse):
        prog = parse("sub f()\n  return 42\nend")
        ret = prog.statements[0].body[0]
        assert isinstance(ret, ReturnStatement)
        assert isinstance(ret.value, NumberLiteral)

    def test_return_no_value(self, parse):
        prog = parse("sub f()\n  return\nend")
        ret = prog.statements[0].body[0]
        assert isinstance(ret, ReturnStatement)
        assert ret.value is None


class TestCallStatement:
    def test_no_args(self, parse):
        prog = parse("greet()")
        stmt = prog.statements[0]
        assert isinstance(stmt, CallStatement)
        assert stmt.name == "greet"
        assert stmt.arguments == []

    def test_with_args(self, parse):
        prog = parse("add(1, 2)")
        stmt = prog.statements[0]
        assert isinstance(stmt, CallStatement)
        assert len(stmt.arguments) == 2


class TestIndexAssignment:
    def test_index_assignment(self, parse):
        prog = parse("mylist[0] = 99")
        stmt = prog.statements[0]
        assert isinstance(stmt, IndexAssignment)
        assert stmt.target == "mylist"


class TestExpressions:
    def test_binary_addition(self, parse):
        prog = parse("x = 1 + 2")
        expr = prog.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "+"

    def test_operator_precedence_mul_over_add(self, parse):
        prog = parse("x = 1 + 2 * 3")
        expr = prog.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "+"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "*"

    def test_operator_precedence_power(self, parse):
        prog = parse("x = 2 ^ 3")
        expr = prog.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "^"

    def test_unary_minus(self, parse):
        prog = parse("x = -5")
        expr = prog.statements[0].value
        assert isinstance(expr, UnaryOp)
        assert expr.operator == "-"

    def test_not_operator(self, parse):
        prog = parse("x = not true")
        expr = prog.statements[0].value
        assert isinstance(expr, UnaryOp)
        assert expr.operator == "not"

    def test_comparison(self, parse):
        prog = parse("x = a == b")
        expr = prog.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "=="

    def test_logical_and(self, parse):
        prog = parse("x = a and b")
        expr = prog.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "and"

    def test_logical_or(self, parse):
        prog = parse("x = a or b")
        expr = prog.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "or"

    def test_grouped_expression(self, parse):
        prog = parse("x = (1 + 2) * 3")
        expr = prog.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "*"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "+"

    def test_function_call_expression(self, parse):
        prog = parse("x = len(mylist)")
        expr = prog.statements[0].value
        assert isinstance(expr, FunctionCall)
        assert expr.name == "len"

    def test_index_access(self, parse):
        prog = parse("x = mylist[0]")
        expr = prog.statements[0].value
        assert isinstance(expr, IndexAccess)
        assert expr.target == "mylist"

    def test_list_literal(self, parse):
        prog = parse("x = [1, 2, 3]")
        expr = prog.statements[0].value
        assert isinstance(expr, ListLiteral)
        assert len(expr.elements) == 3

    def test_empty_list(self, parse):
        prog = parse("x = []")
        expr = prog.statements[0].value
        assert isinstance(expr, ListLiteral)
        assert len(expr.elements) == 0

    def test_null_literal(self, parse):
        prog = parse("x = null")
        expr = prog.statements[0].value
        assert isinstance(expr, NullLiteral)

    def test_boolean_true(self, parse):
        prog = parse("x = true")
        expr = prog.statements[0].value
        assert isinstance(expr, BooleanLiteral)
        assert expr.value is True

    def test_boolean_false(self, parse):
        prog = parse("x = false")
        expr = prog.statements[0].value
        assert isinstance(expr, BooleanLiteral)
        assert expr.value is False


class TestInputExpression:
    def test_input_in_expression(self, parse):
        prog = parse('x = input("prompt: ")')
        expr = prog.statements[0].value
        assert isinstance(expr, FunctionCall)
        assert expr.name == "input"


class TestParseErrors:
    def test_missing_end(self, parse):
        with pytest.raises(BareParseError, match="expected 'end'"):
            parse("if true\n  print 1")

    def test_missing_rparen(self, parse):
        with pytest.raises(BareParseError):
            parse("greet(")

    def test_unexpected_token(self, parse):
        with pytest.raises(BareParseError):
            parse("+ 5")
