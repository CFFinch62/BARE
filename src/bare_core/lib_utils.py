"""Utilities for slicing a BARE source file into its top-level sub blocks.

Used by the IDE's personal-library feature: saving a sub to the user's
library needs to find-and-replace one named block by its exact source text
(so an updated version overwrites the old one instead of duplicating it),
and the library panel needs the same block list to show what's available.
"""

from typing import Dict, List, Tuple

from .lexer import Lexer
from .tokens import TokenType


def extract_sub_blocks(source: str) -> Dict[str, str]:
    """Return {sub_name: exact_source_text} for each top-level `sub...end` block.

    Walks the token stream (rather than the AST) so the returned text is an
    exact slice of the original source, comments and blank lines included.
    Nesting is tracked so a sub containing an `if`/`while` doesn't get cut
    off at the inner `end` — only a block that closes back out to depth 0
    counts as a top-level sub.
    """
    tokens = Lexer(source).tokenize()
    lines = source.splitlines()

    blocks: Dict[str, str] = {}
    stack: List[Tuple[TokenType, int, str]] = []  # (opener type, start line, sub name)

    for i, token in enumerate(tokens):
        if token.type in (TokenType.SUB, TokenType.IF, TokenType.WHILE):
            name = ""
            if token.type == TokenType.SUB and i + 1 < len(tokens):
                name = tokens[i + 1].value
            stack.append((token.type, token.line, name))
        elif token.type == TokenType.END and stack:
            opener_type, start_line, name = stack.pop()
            if opener_type == TokenType.SUB and not stack:
                blocks[name] = "\n".join(lines[start_line - 1 : token.line])

    return blocks
