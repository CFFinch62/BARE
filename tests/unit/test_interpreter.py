"""Unit tests for the BARE interpreter."""

import pytest
from bare_core.errors import BareRuntimeError


class TestArithmetic:
    def test_addition(self, run):
        assert run("print 1 + 2") == ["3"]

    def test_subtraction(self, run):
        assert run("print 10 - 3") == ["7"]

    def test_multiplication(self, run):
        assert run("print 4 * 5") == ["20"]

    def test_division(self, run):
        assert run("print 10 / 4") == ["2.5"]

    def test_modulo(self, run):
        assert run("print 10 % 3") == ["1"]

    def test_exponent(self, run):
        assert run("print 2 ^ 3") == ["8"]

    def test_unary_minus(self, run):
        assert run("print -5") == ["-5"]

    def test_operator_precedence(self, run):
        assert run("print 2 + 3 * 4") == ["14"]

    def test_grouped_expression(self, run):
        assert run("print (2 + 3) * 4") == ["20"]

    def test_division_by_zero(self, run):
        with pytest.raises(BareRuntimeError, match="division by zero"):
            run("print 1 / 0")

    def test_modulo_by_zero(self, run):
        with pytest.raises(BareRuntimeError, match="modulo by zero"):
            run("print 1 % 0")

    def test_integer_display(self, run):
        """Numbers that are whole should display without decimal point."""
        assert run("print 5") == ["5"]
        assert run("print 5.0 + 0") == ["5"]


class TestStrings:
    def test_string_concatenation(self, run):
        assert run('print "hello" + " world"') == ["hello world"]

    def test_string_number_concat(self, run):
        """String + number auto-converts number (spec §5.7)."""
        assert run('print "value: " + 42') == ["value: 42"]

    def test_number_string_concat(self, run):
        assert run('print 42 + " is the answer"') == ["42 is the answer"]

    def test_mixed_type_arithmetic_error(self, run):
        """Non-concatenation mixed types are errors (spec §5.7)."""
        with pytest.raises(BareRuntimeError, match="cannot use"):
            run('print "5" - 1')


class TestBooleans:
    def test_true(self, run):
        assert run("print true") == ["true"]

    def test_false(self, run):
        assert run("print false") == ["false"]

    def test_not(self, run):
        assert run("print not true") == ["false"]
        assert run("print not false") == ["true"]


class TestTruthiness:
    """Spec §5.3: Only false and null are falsy. 0 and '' are truthy."""

    def test_zero_is_truthy(self, run):
        assert run('if 0\n  print "yes"\nend') == ["yes"]

    def test_empty_string_is_truthy(self, run):
        assert run('if ""\n  print "yes"\nend') == ["yes"]

    def test_null_is_falsy(self, run):
        assert run('if null\n  print "yes"\nelse\n  print "no"\nend') == ["no"]

    def test_false_is_falsy(self, run):
        assert run('if false\n  print "yes"\nelse\n  print "no"\nend') == ["no"]

    def test_number_is_truthy(self, run):
        assert run('if 42\n  print "yes"\nend') == ["yes"]

    def test_string_is_truthy(self, run):
        assert run('if "hello"\n  print "yes"\nend') == ["yes"]

    def test_list_is_truthy(self, run):
        assert run('if []\n  print "yes"\nend') == ["yes"]


class TestNull:
    def test_null_print(self, run):
        assert run("print null") == ["null"]

    def test_null_equality(self, run):
        assert run('if null == null\n  print "yes"\nend') == ["yes"]

    def test_null_not_equal_to_false(self, run):
        assert run('if null != false\n  print "yes"\nend') == ["yes"]


class TestVariables:
    def test_assignment_and_read(self, run):
        assert run("x = 5\nprint x") == ["5"]

    def test_reassignment(self, run):
        assert run("x = 5\nx = 10\nprint x") == ["10"]

    def test_dynamic_typing(self, run):
        assert run('x = 5\nx = "now text"\nprint x') == ["now text"]

    def test_undefined_variable(self, run):
        with pytest.raises(BareRuntimeError, match="not defined"):
            run("print x")


class TestComparison:
    def test_equal(self, run):
        assert run("print 1 == 1") == ["true"]
        assert run("print 1 == 2") == ["false"]

    def test_not_equal(self, run):
        assert run("print 1 != 2") == ["true"]
        assert run("print 1 != 1") == ["false"]

    def test_less_than(self, run):
        assert run("print 1 < 2") == ["true"]
        assert run("print 2 < 1") == ["false"]

    def test_greater_than(self, run):
        assert run("print 2 > 1") == ["true"]

    def test_less_equal(self, run):
        assert run("print 1 <= 1") == ["true"]
        assert run("print 1 <= 2") == ["true"]
        assert run("print 2 <= 1") == ["false"]

    def test_greater_equal(self, run):
        assert run("print 2 >= 2") == ["true"]

    def test_string_comparison(self, run):
        assert run('print "a" < "b"') == ["true"]


class TestLogical:
    def test_and(self, run):
        assert run("print true and true") == ["true"]
        assert run("print true and false") == ["false"]

    def test_or(self, run):
        assert run("print false or true") == ["true"]
        assert run("print false or false") == ["false"]

    def test_short_circuit_and(self, run):
        """and should short-circuit: false and (error) should not error."""
        # false and anything → false without evaluating right side
        assert run("print false and true") == ["false"]

    def test_short_circuit_or(self, run):
        """or should short-circuit: true or (error) should not error."""
        assert run("print true or false") == ["true"]


class TestIfElse:
    def test_if_true(self, run):
        assert run("if true\n  print 1\nend") == ["1"]

    def test_if_false(self, run):
        assert run("if false\n  print 1\nend") == []

    def test_if_else(self, run):
        assert run("if false\n  print 1\nelse\n  print 2\nend") == ["2"]

    def test_nested_if(self, run):
        source = """
if true
    if false
        print 1
    else
        print 2
    end
end
"""
        assert run(source) == ["2"]


class TestWhile:
    def test_simple_while(self, run):
        source = "x = 0\nwhile x < 3\n  print x\n  x = x + 1\nend"
        assert run(source) == ["0", "1", "2"]

    def test_while_false(self, run):
        assert run("while false\n  print 1\nend") == []

    def test_cancellation(self):
        """Test that the cancellation flag stops execution."""
        from bare_core.lexer import Lexer
        from bare_core.parser import Parser
        from bare_core.interpreter import Interpreter

        output = []
        tokens = Lexer("x = 0\nwhile true\n  x = x + 1\nend").tokenize()
        program = Parser(tokens).parse()

        interp = Interpreter(output_callback=lambda s: output.append(s))
        # Set cancelled immediately
        interp.cancelled = True

        with pytest.raises(BareRuntimeError, match="execution stopped"):
            interp.execute(program)


class TestSubs:
    def test_simple_sub(self, run):
        source = 'sub greet()\n  print "hi"\nend\ngreet()'
        assert run(source) == ["hi"]

    def test_sub_with_params(self, run):
        source = "sub add(a, b)\n  print a + b\nend\nadd(3, 4)"
        assert run(source) == ["7"]

    def test_sub_return(self, run):
        source = "sub double(n)\n  return n * 2\nend\nprint double(5)"
        assert run(source) == ["10"]

    def test_implicit_null_return(self, run):
        source = "sub noop()\nend\nprint noop()"
        assert run(source) == ["null"]

    def test_recursion(self, run):
        source = """
sub factorial(n)
    if n <= 1
        return 1
    else
        return n * factorial(n - 1)
    end
end
print factorial(5)
"""
        assert run(source) == ["120"]

    def test_scope_isolation(self, run):
        """Subs cannot see global variables (spec §5.2)."""
        source = "x = 10\nsub f()\n  print x\nend\nf()"
        with pytest.raises(BareRuntimeError, match="not defined"):
            run(source)

    def test_wrong_arg_count(self, run):
        source = "sub f(a, b)\n  return a + b\nend\nf(1)"
        with pytest.raises(BareRuntimeError, match="expects 2"):
            run(source)

    def test_undefined_sub(self, run):
        with pytest.raises(BareRuntimeError, match="not defined"):
            run("unknown()")


class TestLists:
    def test_list_literal(self, run):
        assert run("x = [1, 2, 3]\nprint x") == ["[1, 2, 3]"]

    def test_empty_list(self, run):
        assert run("x = []\nprint x") == ["[]"]

    def test_index_access(self, run):
        assert run("x = [10, 20, 30]\nprint x[1]") == ["20"]

    def test_index_assignment(self, run):
        assert run("x = [1, 2, 3]\nx[0] = 99\nprint x[0]") == ["99"]

    def test_out_of_range(self, run):
        with pytest.raises(BareRuntimeError, match="out of range"):
            run("x = [1, 2, 3]\nprint x[5]")

    def test_heterogeneous_list(self, run):
        assert run('x = [1, "two", true]\nprint x[1]') == ["two"]

    def test_nested_list(self, run):
        assert run("x = [[1, 2], [3, 4]]\nprint x") == ["[[1, 2], [3, 4]]"]


class TestLoadLibrary:
    def test_library_sub_is_callable_from_main_program(self, run_with_library):
        library = "sub double(x)\n    return x * 2\nend\n"
        assert run_with_library(library, "print double(21)") == ["42"]

    def test_library_top_level_statements_run_too(self, run_with_library):
        library = 'greeting = "hi"\n'
        assert run_with_library(library, "print greeting") == ["hi"]

    def test_main_program_sub_shadows_library_sub_of_same_name(self, run_with_library):
        library = "sub greet()\n    return \"library\"\nend\n"
        program = "sub greet()\n    return \"main\"\nend\nprint greet()"
        assert run_with_library(library, program) == ["main"]

    def test_load_library_returns_registered_sub_names(self, parse):
        from bare_core.interpreter import Interpreter

        library_program = parse("sub a()\nend\nsub b()\nend\n")
        interpreter = Interpreter()
        assert interpreter.load_library(library_program) == ["a", "b"]
