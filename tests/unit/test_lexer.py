"""Unit tests for the BARE lexer."""

import pytest
from bare_core.lexer import Lexer
from bare_core.tokens import TokenType
from bare_core.errors import BareLexerError


class TestNumbers:
    def test_integer(self, lex):
        tokens = lex("42")
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42.0

    def test_decimal(self, lex):
        tokens = lex("3.14")
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14

    def test_zero(self, lex):
        tokens = lex("0")
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 0.0

    def test_large_number(self, lex):
        tokens = lex("999999")
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 999999.0


class TestStrings:
    def test_simple_string(self, lex):
        tokens = lex('"hello"')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_empty_string(self, lex):
        tokens = lex('""')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == ""

    def test_escape_newline(self, lex):
        tokens = lex(r'"line1\nline2"')
        assert tokens[0].value == "line1\nline2"

    def test_escape_tab(self, lex):
        tokens = lex(r'"col1\tcol2"')
        assert tokens[0].value == "col1\tcol2"

    def test_escape_quote(self, lex):
        tokens = lex(r'"say \"hi\""')
        assert tokens[0].value == 'say "hi"'

    def test_escape_backslash(self, lex):
        tokens = lex(r'"path\\file"')
        assert tokens[0].value == "path\\file"

    def test_unterminated_string(self, lex):
        with pytest.raises(BareLexerError, match="unterminated string"):
            lex('"hello')

    def test_newline_in_string(self, lex):
        with pytest.raises(BareLexerError, match="unterminated string"):
            lex('"hello\nworld"')


class TestKeywords:
    @pytest.mark.parametrize("keyword,token_type", [
        ("print", TokenType.PRINT),
        ("input", TokenType.INPUT),
        ("if", TokenType.IF),
        ("else", TokenType.ELSE),
        ("end", TokenType.END),
        ("while", TokenType.WHILE),
        ("sub", TokenType.SUB),
        ("return", TokenType.RETURN),
        ("and", TokenType.AND),
        ("or", TokenType.OR),
        ("not", TokenType.NOT),
    ])
    def test_keywords(self, lex, keyword, token_type):
        tokens = lex(keyword)
        assert tokens[0].type == token_type

    def test_true_is_literal(self, lex):
        tokens = lex("true")
        assert tokens[0].type == TokenType.TRUE

    def test_false_is_literal(self, lex):
        tokens = lex("false")
        assert tokens[0].type == TokenType.FALSE

    def test_null_is_literal(self, lex):
        tokens = lex("null")
        assert tokens[0].type == TokenType.NULL


class TestIdentifiers:
    def test_simple_identifier(self, lex):
        tokens = lex("count")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "count"

    def test_underscore_identifier(self, lex):
        tokens = lex("my_var")
        assert tokens[0].type == TokenType.IDENTIFIER

    def test_identifier_with_digits(self, lex):
        tokens = lex("x2")
        assert tokens[0].type == TokenType.IDENTIFIER

    def test_case_sensitive(self, lex):
        tokens = lex("Count")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "Count"


class TestOperators:
    @pytest.mark.parametrize("op,token_type", [
        ("+", TokenType.PLUS),
        ("-", TokenType.MINUS),
        ("*", TokenType.STAR),
        ("/", TokenType.SLASH),
        ("%", TokenType.PERCENT),
        ("^", TokenType.CARET),
        ("=", TokenType.EQ),
        ("<", TokenType.LT),
        (">", TokenType.GT),
        ("(", TokenType.LPAREN),
        (")", TokenType.RPAREN),
        ("[", TokenType.LBRACKET),
        ("]", TokenType.RBRACKET),
        (",", TokenType.COMMA),
    ])
    def test_single_char_operators(self, lex, op, token_type):
        # Need an identifier before some ops to avoid ambiguity
        tokens = lex(f"x {op} y")
        assert any(t.type == token_type for t in tokens)

    @pytest.mark.parametrize("op,token_type", [
        ("==", TokenType.EQEQ),
        ("!=", TokenType.BANGEQ),
        ("<=", TokenType.LTEQ),
        (">=", TokenType.GTEQ),
    ])
    def test_two_char_operators(self, lex, op, token_type):
        tokens = lex(f"x {op} y")
        assert any(t.type == token_type for t in tokens)


class TestComments:
    def test_full_line_comment(self, lex):
        tokens = lex("# this is a comment")
        # Should only have NEWLINE + EOF (or just EOF)
        non_structural = [t for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)]
        assert len(non_structural) == 0

    def test_comment_after_code(self, lex):
        tokens = lex("x = 5 # assignment")
        ident = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        assert len(ident) == 1
        assert ident[0].value == "x"


class TestNewlines:
    def test_newline_between_statements(self, lex):
        tokens = lex("x = 1\ny = 2")
        newlines = [t for t in tokens if t.type == TokenType.NEWLINE]
        assert len(newlines) >= 1

    def test_multiple_blank_lines(self, lex):
        tokens = lex("x = 1\n\n\ny = 2")
        # Should collapse to at most one newline between statements
        # (consecutive newlines don't stack)
        non_eof = [t for t in tokens if t.type != TokenType.EOF]
        consecutive_newlines = 0
        max_consecutive = 0
        for t in non_eof:
            if t.type == TokenType.NEWLINE:
                consecutive_newlines += 1
                max_consecutive = max(max_consecutive, consecutive_newlines)
            else:
                consecutive_newlines = 0
        assert max_consecutive <= 1

    def test_eof_token(self, lex):
        tokens = lex("x = 1")
        assert tokens[-1].type == TokenType.EOF


class TestLineTracking:
    def test_line_numbers(self, lex):
        tokens = lex("x = 1\ny = 2")
        x_token = tokens[0]
        assert x_token.line == 1

        # Find the 'y' token
        y_tokens = [t for t in tokens if t.type == TokenType.IDENTIFIER and t.value == "y"]
        assert len(y_tokens) == 1
        assert y_tokens[0].line == 2


class TestEdgeCases:
    def test_empty_source(self, lex):
        tokens = lex("")
        assert tokens[-1].type == TokenType.EOF

    def test_whitespace_only(self, lex):
        tokens = lex("   \t  ")
        assert tokens[-1].type == TokenType.EOF

    def test_unknown_character(self, lex):
        with pytest.raises(BareLexerError, match="unexpected character"):
            lex("@")
