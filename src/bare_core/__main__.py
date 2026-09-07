"""BARE CLI Harness — development convenience.

Run BARE programs straight from a source checkout:
    python -m bare_core myfile.bare

This is the in-tree harness, kept for working on bare_core without
building anything. The shipped console runtime is ../../bare_cli.py,
packaged by installer/bare_cli.spec into `dist/bare` — that is what
MyCode and the VS Code extension launch, and the two behave identically.

The BARE IDE remains the primary way to run .bare files: it is the only
one with scope boxes, breakpoints and the Variable Watch panel.
"""

import sys
from pathlib import Path

from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .errors import BareError


def main() -> int:
    """Run a .bare file from the command line."""
    if len(sys.argv) < 2:
        print("Usage: python -m bare_core <file.bare>", file=sys.stderr)
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
