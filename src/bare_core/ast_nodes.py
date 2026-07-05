"""BARE Abstract Syntax Tree Node Definitions.

Every node includes a `line` attribute for error reporting and IDE
current-line highlighting.

Node Categories:
- Program:     Program
- Literals:    NumberLiteral, StringLiteral, BooleanLiteral, NullLiteral, ListLiteral
- Expressions: BinaryOp, UnaryOp, Identifier, IndexAccess, FunctionCall
- Statements:  Assignment, IndexAssignment, PrintStatement, IfStatement,
               WhileStatement, SubDefinition, ReturnStatement, CallStatement
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional


# =============================================================================
# Base Classes
# =============================================================================


@dataclass
class ASTNode:
    """Base class for all AST nodes."""

    line: int


@dataclass
class Expression(ASTNode):
    """Base class for nodes that produce a value."""

    pass


@dataclass
class Statement(ASTNode):
    """Base class for nodes that perform an action."""

    pass


# =============================================================================
# Literal Expressions
# =============================================================================


@dataclass
class NumberLiteral(Expression):
    """A numeric literal (e.g., 5, 3.14)."""

    value: float


@dataclass
class StringLiteral(Expression):
    """A string literal (e.g., "hello")."""

    value: str


@dataclass
class BooleanLiteral(Expression):
    """A boolean literal (true or false)."""

    value: bool


@dataclass
class NullLiteral(Expression):
    """The null literal."""

    pass


@dataclass
class ListLiteral(Expression):
    """A list literal (e.g., [1, 2, 3])."""

    elements: List[Expression]


# =============================================================================
# Compound Expressions
# =============================================================================


@dataclass
class Identifier(Expression):
    """A variable reference (e.g., x, count)."""

    name: str


@dataclass
class BinaryOp(Expression):
    """A binary operation (e.g., a + b, x == 5)."""

    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOp(Expression):
    """A unary operation (e.g., -x, not flag)."""

    operator: str
    operand: Expression


@dataclass
class IndexAccess(Expression):
    """List index access (e.g., mylist[0])."""

    target: str  # identifier name
    index: Expression


@dataclass
class FunctionCall(Expression):
    """Function/sub call as an expression (e.g., len(x), factorial(5))."""

    name: str
    arguments: List[Expression]


# =============================================================================
# Statements
# =============================================================================


@dataclass
class Assignment(Statement):
    """Variable assignment (e.g., x = 5)."""

    name: str
    value: Expression


@dataclass
class IndexAssignment(Statement):
    """List index assignment (e.g., mylist[0] = 99)."""

    target: str  # identifier name
    index: Expression
    value: Expression


@dataclass
class PrintStatement(Statement):
    """Print statement (e.g., print "hello")."""

    expression: Expression


@dataclass
class IfStatement(Statement):
    """If/else statement.

    if condition
        body...
    else            (optional)
        else_body...
    end
    """

    condition: Expression
    body: List[Statement]
    else_body: List[Statement] = field(default_factory=list)


@dataclass
class WhileStatement(Statement):
    """While loop.

    while condition
        body...
    end
    """

    condition: Expression
    body: List[Statement]


@dataclass
class SubDefinition(Statement):
    """Subroutine definition.

    sub name(param1, param2)
        body...
    end
    """

    name: str
    params: List[str]
    body: List[Statement]


@dataclass
class ReturnStatement(Statement):
    """Return statement (e.g., return x, return).

    value is None if the statement is just `return` with no expression.
    """

    value: Optional[Expression] = None


@dataclass
class CallStatement(Statement):
    """A subroutine/function call used as a statement (e.g., append(list, 5)).

    Semantically identical to FunctionCall but used where the return value
    is discarded.
    """

    name: str
    arguments: List[Expression]


# =============================================================================
# Program Root
# =============================================================================


@dataclass
class Program(ASTNode):
    """The root node — a complete BARE program is a list of statements."""

    statements: List[Statement]
