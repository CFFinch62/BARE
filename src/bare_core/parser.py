"""BARE Parser — Recursive-Descent Parser.

Implements the EBNF grammar from spec §4 with operator precedence
from §6. Produces an AST (Program node) from a token stream.

Grammar summary:
    program     ::= statement*
    statement   ::= assignment | print_stmt | if_stmt | while_stmt
                  | sub_def | return_stmt | call_stmt
    expression  ::= or_expr
    or_expr     ::= and_expr ("or" and_expr)*
    and_expr    ::= not_expr ("and" not_expr)*
    not_expr    ::= "not" not_expr | comparison
    comparison  ::= additive (("==" | "!=" | "<" | ">" | "<=" | ">=") additive)*
    additive    ::= multiplicative (("+" | "-") multiplicative)*
    multiplicative ::= unary (("*" | "/" | "%") unary)*
    unary       ::= "-" unary | power
    power       ::= primary ("^" unary)?
    primary     ::= NUMBER | STRING | "true" | "false" | "null"
                  | identifier | identifier "[" expr "]"
                  | identifier "(" args? ")" | "[" args? "]"
                  | "(" expression ")"
"""

from typing import List, Optional

from .ast_nodes import (
    ASTNode,
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
from .errors import BareParseError, SourceLocation
from .tokens import Token, TokenType


class Parser:
    """Recursive-descent parser for BARE.

    Usage:
        parser = Parser(tokens)
        program = parser.parse()
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Token:
        """Return the current token."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]

    def _peek(self) -> TokenType:
        """Return the current token's type."""
        return self._current().type

    def _peek_ahead(self, offset: int = 1) -> TokenType:
        """Return a future token's type."""
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return TokenType.EOF
        return self.tokens[idx].type

    def _advance(self) -> Token:
        """Consume and return the current token."""
        token = self._current()
        self.pos += 1
        return token

    def _expect(self, token_type: TokenType, message: str = "") -> Token:
        """Consume a token of the expected type, or raise a parse error."""
        if self._peek() != token_type:
            current = self._current()
            if not message:
                message = f"expected {token_type.name}, got {current.type.name} ({current.value!r})"
            raise BareParseError(message, SourceLocation(current.line, current.column))
        return self._advance()

    def _match(self, *types: TokenType) -> Optional[Token]:
        """Consume the current token if it matches any of the given types."""
        if self._peek() in types:
            return self._advance()
        return None

    def _skip_newlines(self) -> None:
        """Skip over any NEWLINE tokens."""
        while self._peek() == TokenType.NEWLINE:
            self._advance()

    def _error(self, message: str) -> BareParseError:
        """Create a parse error at the current position."""
        current = self._current()
        return BareParseError(message, SourceLocation(current.line, current.column))

    # =========================================================================
    # Top-Level
    # =========================================================================

    def parse(self) -> Program:
        """Parse the full token stream into a Program AST."""
        self._skip_newlines()
        statements = self._parse_statement_list()
        self._expect(TokenType.EOF, "expected end of file")
        line = self.tokens[0].line if self.tokens else 1
        return Program(line=line, statements=statements)

    def _parse_statement_list(self, terminators: tuple = ()) -> List[Statement]:
        """Parse statements until a terminator token or EOF.

        Args:
            terminators: Token types that end this block (e.g., END, ELSE).
        """
        statements: List[Statement] = []
        while self._peek() not in (TokenType.EOF, *terminators):
            self._skip_newlines()
            if self._peek() in (TokenType.EOF, *terminators):
                break
            stmt = self._parse_statement()
            statements.append(stmt)
            # Consume statement-ending newline (or allow EOF)
            if self._peek() == TokenType.NEWLINE:
                self._advance()
            elif self._peek() not in (TokenType.EOF, *terminators):
                raise self._error(
                    f"expected newline after statement, got {self._current().type.name}"
                )
            self._skip_newlines()
        return statements

    # =========================================================================
    # Statements
    # =========================================================================

    def _parse_statement(self) -> Statement:
        """Parse a single statement."""
        tt = self._peek()

        if tt == TokenType.PRINT:
            return self._parse_print()
        elif tt == TokenType.IF:
            return self._parse_if()
        elif tt == TokenType.WHILE:
            return self._parse_while()
        elif tt == TokenType.SUB:
            return self._parse_sub()
        elif tt == TokenType.RETURN:
            return self._parse_return()
        elif tt == TokenType.IDENTIFIER:
            return self._parse_identifier_statement()
        else:
            raise self._error(f"unexpected token: {self._current().value!r}")

    def _parse_print(self) -> PrintStatement:
        """Parse: print expression"""
        token = self._advance()  # consume 'print'
        expr = self._parse_expression()
        return PrintStatement(line=token.line, expression=expr)

    def _parse_if(self) -> IfStatement:
        """Parse: if condition NEWLINE body (else NEWLINE body)? end"""
        token = self._advance()  # consume 'if'
        condition = self._parse_expression()
        self._expect(TokenType.NEWLINE, "expected newline after 'if' condition")
        self._skip_newlines()

        body = self._parse_statement_list(terminators=(TokenType.ELSE, TokenType.END))

        else_body: List[Statement] = []
        if self._peek() == TokenType.ELSE:
            self._advance()  # consume 'else'
            self._expect(TokenType.NEWLINE, "expected newline after 'else'")
            self._skip_newlines()
            else_body = self._parse_statement_list(terminators=(TokenType.END,))

        self._expect(TokenType.END, "expected 'end' to close 'if' block")

        return IfStatement(
            line=token.line,
            condition=condition,
            body=body,
            else_body=else_body,
        )

    def _parse_while(self) -> WhileStatement:
        """Parse: while condition NEWLINE body end"""
        token = self._advance()  # consume 'while'
        condition = self._parse_expression()
        self._expect(TokenType.NEWLINE, "expected newline after 'while' condition")
        self._skip_newlines()

        body = self._parse_statement_list(terminators=(TokenType.END,))
        self._expect(TokenType.END, "expected 'end' to close 'while' block")

        return WhileStatement(line=token.line, condition=condition, body=body)

    def _parse_sub(self) -> SubDefinition:
        """Parse: sub name(param1, param2) NEWLINE body end"""
        token = self._advance()  # consume 'sub'
        name_token = self._expect(TokenType.IDENTIFIER, "expected subroutine name after 'sub'")
        self._expect(TokenType.LPAREN, "expected '(' after subroutine name")

        params: List[str] = []
        if self._peek() != TokenType.RPAREN:
            param = self._expect(TokenType.IDENTIFIER, "expected parameter name")
            params.append(param.value)
            while self._match(TokenType.COMMA):
                param = self._expect(TokenType.IDENTIFIER, "expected parameter name after ','")
                params.append(param.value)

        self._expect(TokenType.RPAREN, "expected ')' after parameters")
        self._expect(TokenType.NEWLINE, "expected newline after sub declaration")
        self._skip_newlines()

        body = self._parse_statement_list(terminators=(TokenType.END,))
        self._expect(TokenType.END, "expected 'end' to close 'sub' block")

        return SubDefinition(
            line=token.line,
            name=name_token.value,
            params=params,
            body=body,
        )

    def _parse_return(self) -> ReturnStatement:
        """Parse: return expression?"""
        token = self._advance()  # consume 'return'

        # return with no expression (next is newline or EOF)
        if self._peek() in (TokenType.NEWLINE, TokenType.EOF):
            return ReturnStatement(line=token.line, value=None)

        expr = self._parse_expression()
        return ReturnStatement(line=token.line, value=expr)

    def _parse_identifier_statement(self) -> Statement:
        """Parse a statement starting with an identifier.

        Could be:
          - assignment:       name = expr
          - index assignment: name[expr] = expr
          - function call:    name(args)
        """
        name_token = self._advance()  # consume identifier
        name = name_token.value
        line = name_token.line

        # --- Assignment: name = expr ---
        if self._peek() == TokenType.EQ:
            self._advance()  # consume '='
            value = self._parse_expression()
            return Assignment(line=line, name=name, value=value)

        # --- Index assignment: name[expr] = expr ---
        if self._peek() == TokenType.LBRACKET:
            self._advance()  # consume '['
            index = self._parse_expression()
            self._expect(TokenType.RBRACKET, "expected ']' after index")
            self._expect(TokenType.EQ, "expected '=' in index assignment")
            value = self._parse_expression()
            return IndexAssignment(line=line, target=name, index=index, value=value)

        # --- Function call: name(args) ---
        if self._peek() == TokenType.LPAREN:
            self._advance()  # consume '('
            args = self._parse_arg_list()
            self._expect(TokenType.RPAREN, "expected ')' after arguments")
            return CallStatement(line=line, name=name, arguments=args)

        raise BareParseError(
            f"expected '=', '[', or '(' after identifier '{name}'",
            SourceLocation(line, name_token.column),
        )

    # =========================================================================
    # Expressions (Precedence Climbing)
    # =========================================================================

    def _parse_expression(self) -> Expression:
        """Parse an expression (entry point — lowest precedence)."""
        return self._parse_or()

    def _parse_or(self) -> Expression:
        """Parse: and_expr ("or" and_expr)*"""
        left = self._parse_and()
        while self._peek() == TokenType.OR:
            op_token = self._advance()
            right = self._parse_and()
            left = BinaryOp(line=op_token.line, left=left, operator="or", right=right)
        return left

    def _parse_and(self) -> Expression:
        """Parse: not_expr ("and" not_expr)*"""
        left = self._parse_not()
        while self._peek() == TokenType.AND:
            op_token = self._advance()
            right = self._parse_not()
            left = BinaryOp(line=op_token.line, left=left, operator="and", right=right)
        return left

    def _parse_not(self) -> Expression:
        """Parse: "not" not_expr | comparison"""
        if self._peek() == TokenType.NOT:
            op_token = self._advance()
            operand = self._parse_not()
            return UnaryOp(line=op_token.line, operator="not", operand=operand)
        return self._parse_comparison()

    def _parse_comparison(self) -> Expression:
        """Parse: additive (("==" | "!=" | "<" | ">" | "<=" | ">=") additive)*"""
        left = self._parse_additive()
        comparison_ops = {
            TokenType.EQEQ: "==",
            TokenType.BANGEQ: "!=",
            TokenType.LT: "<",
            TokenType.GT: ">",
            TokenType.LTEQ: "<=",
            TokenType.GTEQ: ">=",
        }
        while self._peek() in comparison_ops:
            op_token = self._advance()
            op_str = comparison_ops[op_token.type]
            right = self._parse_additive()
            left = BinaryOp(line=op_token.line, left=left, operator=op_str, right=right)
        return left

    def _parse_additive(self) -> Expression:
        """Parse: multiplicative (("+" | "-") multiplicative)*"""
        left = self._parse_multiplicative()
        while self._peek() in (TokenType.PLUS, TokenType.MINUS):
            op_token = self._advance()
            op_str = "+" if op_token.type == TokenType.PLUS else "-"
            right = self._parse_multiplicative()
            left = BinaryOp(line=op_token.line, left=left, operator=op_str, right=right)
        return left

    def _parse_multiplicative(self) -> Expression:
        """Parse: unary (("*" | "/" | "%") unary)*"""
        left = self._parse_unary()
        while self._peek() in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self._advance()
            op_map = {TokenType.STAR: "*", TokenType.SLASH: "/", TokenType.PERCENT: "%"}
            right = self._parse_unary()
            left = BinaryOp(
                line=op_token.line, left=left, operator=op_map[op_token.type], right=right
            )
        return left

    def _parse_unary(self) -> Expression:
        """Parse: "-" unary | power"""
        if self._peek() == TokenType.MINUS:
            op_token = self._advance()
            operand = self._parse_unary()
            return UnaryOp(line=op_token.line, operator="-", operand=operand)
        return self._parse_power()

    def _parse_power(self) -> Expression:
        """Parse: primary ("^" unary)?  — right-associative."""
        left = self._parse_primary()
        if self._peek() == TokenType.CARET:
            op_token = self._advance()
            right = self._parse_unary()  # right-associative: recurse into unary, not power
            return BinaryOp(line=op_token.line, left=left, operator="^", right=right)
        return left

    def _parse_primary(self) -> Expression:
        """Parse a primary expression (highest precedence)."""
        token = self._current()

        # --- Number ---
        if token.type == TokenType.NUMBER:
            self._advance()
            return NumberLiteral(line=token.line, value=token.value)

        # --- String ---
        if token.type == TokenType.STRING:
            self._advance()
            return StringLiteral(line=token.line, value=token.value)

        # --- Boolean ---
        if token.type == TokenType.TRUE:
            self._advance()
            return BooleanLiteral(line=token.line, value=True)
        if token.type == TokenType.FALSE:
            self._advance()
            return BooleanLiteral(line=token.line, value=False)

        # --- Null ---
        if token.type == TokenType.NULL:
            self._advance()
            return NullLiteral(line=token.line)

        # --- input as expression: input(prompt) ---
        if token.type == TokenType.INPUT:
            self._advance()
            self._expect(TokenType.LPAREN, "expected '(' after 'input'")
            args = self._parse_arg_list()
            self._expect(TokenType.RPAREN, "expected ')' after input arguments")
            return FunctionCall(line=token.line, name="input", arguments=args)

        # --- Identifier (variable, index access, or function call) ---
        if token.type == TokenType.IDENTIFIER:
            self._advance()

            # Function call: name(args)
            if self._peek() == TokenType.LPAREN:
                self._advance()  # consume '('
                args = self._parse_arg_list()
                self._expect(TokenType.RPAREN, "expected ')' after arguments")
                return FunctionCall(line=token.line, name=token.value, arguments=args)

            # Index access: name[expr]
            if self._peek() == TokenType.LBRACKET:
                self._advance()  # consume '['
                index = self._parse_expression()
                self._expect(TokenType.RBRACKET, "expected ']' after index")
                return IndexAccess(line=token.line, target=token.value, index=index)

            # Plain variable reference
            return Identifier(line=token.line, name=token.value)

        # --- List literal: [expr, expr, ...] ---
        if token.type == TokenType.LBRACKET:
            self._advance()  # consume '['
            elements = self._parse_arg_list()
            self._expect(TokenType.RBRACKET, "expected ']' to close list literal")
            return ListLiteral(line=token.line, elements=elements)

        # --- Grouped expression: (expr) ---
        if token.type == TokenType.LPAREN:
            self._advance()  # consume '('
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, "expected ')' to close grouped expression")
            return expr

        raise self._error(f"unexpected token in expression: {token.value!r}")

    # =========================================================================
    # Helpers
    # =========================================================================

    def _parse_arg_list(self) -> List[Expression]:
        """Parse a comma-separated list of expressions (for function calls and list literals)."""
        args: List[Expression] = []

        # Empty arg list
        if self._peek() in (TokenType.RPAREN, TokenType.RBRACKET):
            return args

        args.append(self._parse_expression())
        while self._match(TokenType.COMMA):
            args.append(self._parse_expression())

        return args
