"""Scope Box Computation for BARE IDE.

BARE has no significant indentation — nesting is expressed with `end`
keywords, not whitespace, so scope boxes can't be inferred the way
Python-style editors do it. Instead this does a simple line-based keyword
scan (if/while/sub open a block, else splits it, end closes it) rather
than a full parse. That's deliberate: a student's editor is in a
syntax-error state more often than not while they're mid-edit, and a box
computation that requires a clean parse would flicker in and out
constantly. A dangling unclosed block here just means fewer boxes show up
— it never raises.
"""

from dataclasses import dataclass
from typing import List

_BLOCK_KEYWORDS = ("if", "while", "sub")


@dataclass
class ScopeBox:
    """One colored region: a block body or an if/else branch.

    Lines are 1-based and inclusive, and exclude the header (`if ...`,
    `else`) and `end` lines themselves — only the body is boxed.
    """

    start_line: int
    end_line: int
    depth: int


def compute_scope_boxes(text: str) -> List[ScopeBox]:
    """Scan source text and return one ScopeBox per block body/branch."""
    boxes: List[ScopeBox] = []
    stack = []  # dicts: {"branch_start": 1-based line, "depth": int}
    depth = 0

    for i, line in enumerate(text.split("\n"), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        first_word = stripped.split(None, 1)[0]

        if first_word in _BLOCK_KEYWORDS:
            stack.append({"branch_start": i + 1, "depth": depth})
            depth += 1
        elif first_word == "else" and stack:
            top = stack[-1]
            if i - 1 >= top["branch_start"]:
                boxes.append(ScopeBox(top["branch_start"], i - 1, top["depth"]))
            top["branch_start"] = i + 1
        elif first_word == "end" and stack:
            top = stack.pop()
            depth -= 1
            if i - 1 >= top["branch_start"]:
                boxes.append(ScopeBox(top["branch_start"], i - 1, top["depth"]))

    return boxes
