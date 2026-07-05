"""BARE Interpreter — Tree-Walking Evaluator.

Executes a BARE AST by walking the tree node-by-node. This is the core
runtime for the language.

Key design decisions:
- Single numeric type (Python float) for all numbers
- Truthiness: only False and None are falsy (0 and "" are truthy — spec §5.3)
- Sub calls get a fresh Environment with NO parent access (spec §5.2)
- String + number auto-converts number to string (spec §5.7)
- All other mixed-type arithmetic is a runtime error
- Cancellation flag checked between statements for cooperative stop
- Step callback hook for the IDE's step-debug mode
"""

from typing import Any, Callable, Dict, List, Optional

from .ast_nodes import (
    Assignment,
    BinaryOp,
    BooleanLiteral,
    CallStatement,
    Expression,
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
    Statement,
    StringLiteral,
    SubDefinition,
    UnaryOp,
    WhileStatement,
)
from .builtins import BUILTINS, _bare_repr
from .environment import Environment
from .errors import BareRuntimeError, SourceLocation


class ReturnSignal(Exception):
    """Internal signal used to unwind the call stack on 'return'.

    Not a user-visible error — caught by the sub-call handler.
    """

    def __init__(self, value: Any):
        self.value = value


class Interpreter:
    """Tree-walking interpreter for BARE programs.

    Attributes:
        global_env: The global scope environment.
        output_callback: Called with a string whenever 'print' executes.
        input_callback: Called with a prompt string when 'input()' is called;
                        must return the user's input as a string.
        step_callback: Called before each statement with (line, env) for
                       step-debug mode. May block (e.g., wait for user click).
        cancelled: Set to True to cooperatively stop execution.
    """

    def __init__(
        self,
        output_callback: Optional[Callable[[str], None]] = None,
        input_callback: Optional[Callable[[str], str]] = None,
        step_callback: Optional[Callable[[int, Environment], None]] = None,
    ):
        self.global_env = Environment()
        self.output_callback = output_callback or (lambda s: print(s))
        self.input_callback = input_callback or (lambda prompt: input(prompt))
        self.step_callback = step_callback
        self.cancelled = False

        # User-defined subs (name → SubDefinition node)
        self._subs: Dict[str, SubDefinition] = {}

    def execute(self, program: Program) -> None:
        """Execute a complete BARE program."""
        self._execute_statements(program.statements, self.global_env)

    def load_library(self, library_program: Program) -> List[str]:
        """Run a personal-library file's top-level statements before the
        main program, so its subs are ordinary callables alongside builtins.

        Returns the names of subs the library registered (for reporting to
        the student). Runs against the same global scope as the main
        program, so a sub the student later redefines simply shadows the
        library's version — no special collision handling needed.
        """
        before = set(self._subs)
        self._execute_statements(library_program.statements, self.global_env)
        return sorted(set(self._subs) - before)

    def _check_cancelled(self) -> None:
        """Check the cancellation flag between statements."""
        if self.cancelled:
            raise BareRuntimeError("execution stopped", SourceLocation(0))

    def _execute_statements(self, statements: List[Statement], env: Environment) -> None:
        """Execute a list of statements in the given environment."""
        for stmt in statements:
            self._check_cancelled()

            # Step-debug hook
            if self.step_callback is not None:
                self.step_callback(stmt.line, env)

            self._execute_statement(stmt, env)

    def _execute_statement(self, stmt: Statement, env: Environment) -> None:
        """Execute a single statement."""
        if isinstance(stmt, PrintStatement):
            self._exec_print(stmt, env)
        elif isinstance(stmt, Assignment):
            self._exec_assignment(stmt, env)
        elif isinstance(stmt, IndexAssignment):
            self._exec_index_assignment(stmt, env)
        elif isinstance(stmt, IfStatement):
            self._exec_if(stmt, env)
        elif isinstance(stmt, WhileStatement):
            self._exec_while(stmt, env)
        elif isinstance(stmt, SubDefinition):
            self._exec_sub_def(stmt, env)
        elif isinstance(stmt, ReturnStatement):
            self._exec_return(stmt, env)
        elif isinstance(stmt, CallStatement):
            self._exec_call_statement(stmt, env)
        else:
            raise BareRuntimeError(
                f"unknown statement type: {type(stmt).__name__}",
                SourceLocation(stmt.line),
            )

    # =========================================================================
    # Statement Execution
    # =========================================================================

    def _exec_print(self, stmt: PrintStatement, env: Environment) -> None:
        """Execute: print expression"""
        value = self._evaluate(stmt.expression, env)
        self.output_callback(_bare_repr(value))

    def _exec_assignment(self, stmt: Assignment, env: Environment) -> None:
        """Execute: name = expression"""
        value = self._evaluate(stmt.value, env)
        env.set(stmt.name, value)

    def _exec_index_assignment(self, stmt: IndexAssignment, env: Environment) -> None:
        """Execute: name[index] = expression"""
        target = env.get(stmt.target, stmt.line)
        if not isinstance(target, list):
            raise BareRuntimeError(
                f"cannot index into {type(target).__name__}",
                SourceLocation(stmt.line),
            )
        index = self._evaluate(stmt.index, env)
        if not isinstance(index, float):
            raise BareRuntimeError(
                "list index must be a number",
                SourceLocation(stmt.line),
            )
        idx = int(index)
        if idx < 0 or idx >= len(target):
            raise BareRuntimeError(
                f"list index {idx} out of range (list has {len(target)} elements)",
                SourceLocation(stmt.line),
            )
        value = self._evaluate(stmt.value, env)
        target[idx] = value

    def _exec_if(self, stmt: IfStatement, env: Environment) -> None:
        """Execute: if/else/end"""
        condition = self._evaluate(stmt.condition, env)
        if self._is_truthy(condition):
            self._execute_statements(stmt.body, env)
        else:
            self._execute_statements(stmt.else_body, env)

    def _exec_while(self, stmt: WhileStatement, env: Environment) -> None:
        """Execute: while/end"""
        while self._is_truthy(self._evaluate(stmt.condition, env)):
            self._check_cancelled()
            self._execute_statements(stmt.body, env)

    def _exec_sub_def(self, stmt: SubDefinition, env: Environment) -> None:
        """Register a subroutine definition (does not execute it)."""
        self._subs[stmt.name] = stmt

    def _exec_return(self, stmt: ReturnStatement, env: Environment) -> None:
        """Execute: return expression?"""
        value = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value, env)
        raise ReturnSignal(value)

    def _exec_call_statement(self, stmt: CallStatement, env: Environment) -> None:
        """Execute a function/sub call as a statement (discard return value)."""
        self._call_function(stmt.name, stmt.arguments, env, stmt.line)

    # =========================================================================
    # Expression Evaluation
    # =========================================================================

    def _evaluate(self, expr: Expression, env: Environment) -> Any:
        """Evaluate an expression and return its value."""
        if isinstance(expr, NumberLiteral):
            return expr.value

        if isinstance(expr, StringLiteral):
            return expr.value

        if isinstance(expr, BooleanLiteral):
            return expr.value

        if isinstance(expr, NullLiteral):
            return None

        if isinstance(expr, ListLiteral):
            return [self._evaluate(e, env) for e in expr.elements]

        if isinstance(expr, Identifier):
            return env.get(expr.name, expr.line)

        if isinstance(expr, BinaryOp):
            return self._eval_binary(expr, env)

        if isinstance(expr, UnaryOp):
            return self._eval_unary(expr, env)

        if isinstance(expr, IndexAccess):
            return self._eval_index_access(expr, env)

        if isinstance(expr, FunctionCall):
            return self._call_function(expr.name, expr.arguments, env, expr.line)

        raise BareRuntimeError(
            f"unknown expression type: {type(expr).__name__}",
            SourceLocation(expr.line),
        )

    def _eval_binary(self, expr: BinaryOp, env: Environment) -> Any:
        """Evaluate a binary operation."""
        # Short-circuit for logical operators
        if expr.operator == "and":
            left = self._evaluate(expr.left, env)
            if not self._is_truthy(left):
                return left
            return self._evaluate(expr.right, env)

        if expr.operator == "or":
            left = self._evaluate(expr.left, env)
            if self._is_truthy(left):
                return left
            return self._evaluate(expr.right, env)

        left = self._evaluate(expr.left, env)
        right = self._evaluate(expr.right, env)

        # --- Comparison operators ---
        if expr.operator == "==":
            return self._values_equal(left, right)
        if expr.operator == "!=":
            return not self._values_equal(left, right)
        if expr.operator in ("<", ">", "<=", ">="):
            return self._compare(left, right, expr.operator, expr.line)

        # --- Arithmetic / string concatenation ---
        if expr.operator == "+":
            return self._add(left, right, expr.line)
        if expr.operator == "-":
            return self._numeric_op(left, right, lambda a, b: a - b, "-", expr.line)
        if expr.operator == "*":
            return self._numeric_op(left, right, lambda a, b: a * b, "*", expr.line)
        if expr.operator == "/":
            if isinstance(right, float) and right == 0:
                raise BareRuntimeError("division by zero", SourceLocation(expr.line))
            return self._numeric_op(left, right, lambda a, b: a / b, "/", expr.line)
        if expr.operator == "%":
            if isinstance(right, float) and right == 0:
                raise BareRuntimeError("modulo by zero", SourceLocation(expr.line))
            return self._numeric_op(left, right, lambda a, b: a % b, "%", expr.line)
        if expr.operator == "^":
            return self._numeric_op(left, right, lambda a, b: a**b, "^", expr.line)

        raise BareRuntimeError(
            f"unknown operator: {expr.operator}",
            SourceLocation(expr.line),
        )

    def _eval_unary(self, expr: UnaryOp, env: Environment) -> Any:
        """Evaluate a unary operation."""
        operand = self._evaluate(expr.operand, env)

        if expr.operator == "-":
            if not isinstance(operand, float):
                raise BareRuntimeError(
                    f"cannot negate {self._type_name(operand)}",
                    SourceLocation(expr.line),
                )
            return -operand

        if expr.operator == "not":
            return not self._is_truthy(operand)

        raise BareRuntimeError(
            f"unknown unary operator: {expr.operator}",
            SourceLocation(expr.line),
        )

    def _eval_index_access(self, expr: IndexAccess, env: Environment) -> Any:
        """Evaluate: name[index]"""
        target = env.get(expr.target, expr.line)
        index = self._evaluate(expr.index, env)

        if isinstance(target, list):
            if not isinstance(index, float):
                raise BareRuntimeError(
                    "list index must be a number",
                    SourceLocation(expr.line),
                )
            idx = int(index)
            if idx < 0 or idx >= len(target):
                raise BareRuntimeError(
                    f"list index {idx} out of range (list has {len(target)} elements)",
                    SourceLocation(expr.line),
                )
            return target[idx]

        if isinstance(target, str):
            if not isinstance(index, float):
                raise BareRuntimeError(
                    "string index must be a number",
                    SourceLocation(expr.line),
                )
            idx = int(index)
            if idx < 0 or idx >= len(target):
                raise BareRuntimeError(
                    f"string index {idx} out of range (string has {len(target)} characters)",
                    SourceLocation(expr.line),
                )
            return target[idx]

        raise BareRuntimeError(
            f"cannot index into {self._type_name(target)}",
            SourceLocation(expr.line),
        )

    # =========================================================================
    # Function/Sub Calls
    # =========================================================================

    def _call_function(
        self,
        name: str,
        arg_exprs: List[Expression],
        env: Environment,
        line: int,
    ) -> Any:
        """Call a builtin function or user-defined sub."""
        args = [self._evaluate(a, env) for a in arg_exprs]

        # --- input() builtin (special: uses input_callback) ---
        if name == "input":
            if len(args) == 0:
                prompt = ""
            elif len(args) == 1:
                prompt = _bare_repr(args[0])
            else:
                raise BareRuntimeError(
                    "'input' expects 0 or 1 argument(s)",
                    SourceLocation(line),
                )
            return self.input_callback(prompt)

        # --- Other builtins ---
        if name in BUILTINS:
            return BUILTINS[name](args, line)

        # --- User-defined subs ---
        if name in self._subs:
            return self._call_sub(self._subs[name], args, line)

        raise BareRuntimeError(
            f"'{name}' is not defined",
            SourceLocation(line),
        )

    def _call_sub(self, sub: SubDefinition, args: List[Any], line: int) -> Any:
        """Call a user-defined subroutine."""
        if len(args) != len(sub.params):
            raise BareRuntimeError(
                f"'{sub.name}' expects {len(sub.params)} argument(s), got {len(args)}",
                SourceLocation(line),
            )

        # Fresh scope — no parent access (spec §5.2)
        sub_env = Environment()
        for param, arg in zip(sub.params, args):
            sub_env.set(param, arg)

        try:
            self._execute_statements(sub.body, sub_env)
        except ReturnSignal as ret:
            return ret.value

        # No explicit return → implicit null (spec §5.5)
        return None

    # =========================================================================
    # Type Helpers
    # =========================================================================

    def _is_truthy(self, value: Any) -> bool:
        """BARE truthiness: only False and None are falsy (spec §5.3).

        0 and "" are truthy — this is a deliberate departure from C-family
        convention, chosen to remove a common beginner surprise.
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def _type_name(self, value: Any) -> str:
        """Return the BARE type name for a value."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, float):
            return "number"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "list"
        return type(value).__name__

    def _values_equal(self, left: Any, right: Any) -> bool:
        """Check equality between two BARE values."""
        # None is only equal to None
        if left is None and right is None:
            return True
        if left is None or right is None:
            return False
        return left == right

    def _add(self, left: Any, right: Any, line: int) -> Any:
        """Handle the + operator with string concatenation coercion (spec §5.7)."""
        # Both numbers → arithmetic
        if isinstance(left, float) and isinstance(right, float):
            return left + right

        # Both strings → concatenate
        if isinstance(left, str) and isinstance(right, str):
            return left + right

        # String + number → auto-convert number to string
        if isinstance(left, str) and isinstance(right, float):
            return left + _bare_repr(right)
        if isinstance(left, float) and isinstance(right, str):
            return _bare_repr(left) + right

        raise BareRuntimeError(
            f"cannot add {self._type_name(left)} and {self._type_name(right)}",
            SourceLocation(line),
        )

    def _numeric_op(
        self,
        left: Any,
        right: Any,
        op: Callable[[float, float], float],
        op_name: str,
        line: int,
    ) -> float:
        """Apply a numeric-only binary operator."""
        if not isinstance(left, float) or not isinstance(right, float):
            raise BareRuntimeError(
                f"cannot use '{op_name}' on {self._type_name(left)} and {self._type_name(right)}",
                SourceLocation(line),
            )
        return op(left, right)

    def _compare(self, left: Any, right: Any, op: str, line: int) -> bool:
        """Compare two values with <, >, <=, >=."""
        if isinstance(left, float) and isinstance(right, float):
            if op == "<":
                return left < right
            if op == ">":
                return left > right
            if op == "<=":
                return left <= right
            if op == ">=":
                return left >= right

        if isinstance(left, str) and isinstance(right, str):
            if op == "<":
                return left < right
            if op == ">":
                return left > right
            if op == "<=":
                return left <= right
            if op == ">=":
                return left >= right

        raise BareRuntimeError(
            f"cannot compare {self._type_name(left)} and {self._type_name(right)} with '{op}'",
            SourceLocation(line),
        )
