"""BARE Lexer — Tokenization Module.

Converts BARE source code into a stream of tokens. Handles:
- Identifiers and keywords (11 reserved words)
- Literal-value keywords (true, false, null)
- Number literals (integers and decimals)
- String literals (double-quoted, with escape sequences)
- Comments (# to end of line)
- All operators including two-character (==, !=, <=, >=)
- NEWLINE tokens as statement delimiters

BARE does NOT use significant whitespace — blocks are delimited by
keywords (if/while/sub ... end), so there is no INDENT/DEDENT logic.
"""

from typing import List

from .errors import BareLexerError, SourceLocation
from .tokens import KEYWORDS, LITERAL_KEYWORDS, Token, TokenType


class Lexer:
    """Tokenize BARE source code.

    Usage:
        lexer = Lexer(source_text)
        tokens = lexer.tokenize()
    """

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def _error(self, message: str) -> BareLexerError:
        """Create a lexer error at the current position."""
        return BareLexerError(message, SourceLocation(self.line, self.column))

    def _peek(self) -> str:
        """Return current character without consuming it, or '\\0' at EOF."""
        if self.pos >= len(self.source):
            return "\0"
        return self.source[self.pos]

    def _peek_next(self) -> str:
        """Return the character after current, or '\\0' at EOF."""
        if self.pos + 1 >= len(self.source):
            return "\0"
        return self.source[self.pos + 1]

    def _advance(self) -> str:
        """Consume and return the current character, updating line/column."""
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _add_token(self, token_type: TokenType, value: object, line: int, column: int) -> None:
        """Append a token to the output list."""
        self.tokens.append(Token(token_type, value, line, column))

    def _skip_whitespace(self) -> None:
        """Skip spaces and tabs (but not newlines — those are tokens)."""
        while self.pos < len(self.source) and self.source[self.pos] in (" ", "\t", "\r"):
            self._advance()

    def _skip_comment(self) -> None:
        """Skip from # to end of line."""
        while self.pos < len(self.source) and self.source[self.pos] != "\n":
            self._advance()

    def _read_string(self) -> None:
        """Read a double-quoted string literal with escape sequences."""
        start_line = self.line
        start_col = self.column
        self._advance()  # consume opening "

        result: list[str] = []
        while self.pos < len(self.source):
            ch = self._peek()
            if ch == '"':
                self._advance()  # consume closing "
                self._add_token(TokenType.STRING, "".join(result), start_line, start_col)
                return
            elif ch == "\\":
                self._advance()  # consume backslash
                escape = self._peek()
                if escape == "n":
                    result.append("\n")
                    self._advance()
                elif escape == "t":
                    result.append("\t")
                    self._advance()
                elif escape == "\\":
                    result.append("\\")
                    self._advance()
                elif escape == '"':
                    result.append('"')
                    self._advance()
                else:
                    # Unknown escape — keep as-is
                    result.append("\\")
                    result.append(escape)
                    self._advance()
            elif ch == "\n":
                raise self._error("unterminated string literal")
            else:
                result.append(ch)
                self._advance()

        raise BareLexerError(
            "unterminated string literal",
            SourceLocation(start_line, start_col),
        )

    def _read_number(self) -> None:
        """Read an integer or decimal number literal."""
        start_line = self.line
        start_col = self.column
        start_pos = self.pos

        # Consume digits
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self._advance()

        # Check for decimal point
        if self.pos < len(self.source) and self.source[self.pos] == ".":
            next_pos = self.pos + 1
            if next_pos < len(self.source) and self.source[next_pos].isdigit():
                self._advance()  # consume '.'
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    self._advance()

        text = self.source[start_pos : self.pos]
        value = float(text) if "." in text else float(text)
        # Store as float uniformly — BARE has one numeric type
        self._add_token(TokenType.NUMBER, value, start_line, start_col)

    def _read_identifier_or_keyword(self) -> None:
        """Read an identifier, keyword, or literal-value keyword."""
        start_line = self.line
        start_col = self.column
        start_pos = self.pos

        while self.pos < len(self.source) and (
            self.source[self.pos].isalnum() or self.source[self.pos] == "_"
        ):
            self._advance()

        text = self.source[start_pos : self.pos]

        # Check keywords first (11 reserved words)
        if text in KEYWORDS:
            self._add_token(KEYWORDS[text], text, start_line, start_col)
        # Then literal-value keywords (true, false, null)
        elif text in LITERAL_KEYWORDS:
            self._add_token(LITERAL_KEYWORDS[text], text, start_line, start_col)
        else:
            self._add_token(TokenType.IDENTIFIER, text, start_line, start_col)

    def tokenize(self) -> List[Token]:
        """Tokenize the entire source, returning a list of tokens ending with EOF."""
        self.tokens = []
        last_was_newline = True  # suppress leading newlines

        while self.pos < len(self.source):
            self._skip_whitespace()

            if self.pos >= len(self.source):
                break

            ch = self._peek()

            # --- Newline ---
            if ch == "\n":
                if not last_was_newline:
                    self._add_token(TokenType.NEWLINE, "\\n", self.line, self.column)
                    last_was_newline = True
                self._advance()
                continue

            last_was_newline = False

            # --- Comment ---
            if ch == "#":
                self._skip_comment()
                continue

            # --- String ---
            if ch == '"':
                self._read_string()
                continue

            # --- Number ---
            if ch.isdigit():
                self._read_number()
                continue

            # --- Identifier / Keyword ---
            if ch.isalpha() or ch == "_":
                self._read_identifier_or_keyword()
                continue

            # --- Two-character operators ---
            line, col = self.line, self.column
            next_ch = self._peek_next()

            if ch == "=" and next_ch == "=":
                self._advance()
                self._advance()
                self._add_token(TokenType.EQEQ, "==", line, col)
                continue
            if ch == "!" and next_ch == "=":
                self._advance()
                self._advance()
                self._add_token(TokenType.BANGEQ, "!=", line, col)
                continue
            if ch == "<" and next_ch == "=":
                self._advance()
                self._advance()
                self._add_token(TokenType.LTEQ, "<=", line, col)
                continue
            if ch == ">" and next_ch == "=":
                self._advance()
                self._advance()
                self._add_token(TokenType.GTEQ, ">=", line, col)
                continue

            # --- Single-character operators ---
            single_char_tokens = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "%": TokenType.PERCENT,
                "^": TokenType.CARET,
                "=": TokenType.EQ,
                "<": TokenType.LT,
                ">": TokenType.GT,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                "[": TokenType.LBRACKET,
                "]": TokenType.RBRACKET,
                ",": TokenType.COMMA,
            }

            if ch in single_char_tokens:
                self._advance()
                self._add_token(single_char_tokens[ch], ch, line, col)
                continue

            # --- Unknown character ---
            raise self._error(f"unexpected character: {ch!r}")

        # Ensure final NEWLINE before EOF (simplifies parser)
        if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
            self._add_token(TokenType.NEWLINE, "\\n", self.line, self.column)

        self._add_token(TokenType.EOF, "", self.line, self.column)
        return self.tokens
