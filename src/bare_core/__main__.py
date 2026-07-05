"""BARE CLI Harness — Temporary Development Tool.

Run BARE programs from the command line:
    python -m bare_core myfile.bare

THIS HARNESS IS DELETED BEFORE RELEASE. BARE is IDE-locked — the
only way end users run .bare files is through the BARE IDE.
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
