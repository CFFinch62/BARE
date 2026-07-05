"""BARE Token Definitions.

Defines all token types for the BARE language and the Token dataclass
that the lexer produces and the parser consumes.

BARE has 11 reserved words:
    print  input  if  else  end  while  sub  return  and  or  not

Literals (true, false, null) are resolved as values, not keywords.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    """All token types in the BARE language."""

    # --- Keywords (11 reserved words) ---
    PRINT = auto()
    INPUT = auto()
    IF = auto()
    ELSE = auto()
    END = auto()
    WHILE = auto()
    SUB = auto()
    RETURN = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # --- Literals ---
    NUMBER = auto()       # 5, 3.14
    STRING = auto()       # "hello"
    TRUE = auto()         # true
    FALSE = auto()        # false
    NULL = auto()         # null

    # --- Identifiers ---
    IDENTIFIER = auto()   # variable/function names

    # --- Arithmetic operators ---
    PLUS = auto()         # +
    MINUS = auto()        # -
    STAR = auto()         # *
    SLASH = auto()        # /
    PERCENT = auto()      # %
    CARET = auto()        # ^

    # --- Comparison operators ---
    EQEQ = auto()        # ==
    BANGEQ = auto()       # !=
    LT = auto()           # <
    GT = auto()           # >
    LTEQ = auto()         # <=
    GTEQ = auto()         # >=

    # --- Assignment ---
    EQ = auto()           # =

    # --- Delimiters ---
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    COMMA = auto()        # ,

    # --- Structure ---
    NEWLINE = auto()      # statement delimiter
    EOF = auto()          # end of file


@dataclass
class Token:
    """A single token produced by the lexer.

    Attributes:
        type: The token's type from the TokenType enum.
        value: The raw string value from source (or converted numeric value).
        line: 1-indexed line number in source.
        column: 1-indexed column number in source.
    """

    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:{self.column})"


# Mapping from keyword strings to their TokenType.
# Checked during identifier tokenization — if an identifier matches a keyword,
# it gets the keyword token type instead of IDENTIFIER.
KEYWORDS: dict[str, TokenType] = {
    "print": TokenType.PRINT,
    "input": TokenType.INPUT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "end": TokenType.END,
    "while": TokenType.WHILE,
    "sub": TokenType.SUB,
    "return": TokenType.RETURN,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}

# Literal value keywords — these produce value tokens, not keyword tokens.
LITERAL_KEYWORDS: dict[str, TokenType] = {
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
}
