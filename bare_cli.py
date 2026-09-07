#!/usr/bin/env python3
"""BARE CLI Interpreter — Standalone executable entrypoint."""

import sys
from pathlib import Path

from bare_core.lexer import Lexer
from bare_core.parser import Parser
from bare_core.interpreter import Interpreter
from bare_core.errors import BareError


def main() -> int:
    if len(sys.argv) < 2:
        print("BARE Language Interpreter v0.1.0")
        print("Usage: bare <file.bare>")
        return 1

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        return 1

    source = filepath.read_text(encoding="utf-8")

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        program = parser.parse()

        interpreter = Interpreter()
        interpreter.execute(program)

    except BareError as e:
        print(e.format(), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
