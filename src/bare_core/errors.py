"""BARE Error Types and Formatting.

Error hierarchy:
    BareError
    ├── BareLexerError    — invalid characters, unterminated strings
    ├── BareParseError    — syntax violations
    └── BareRuntimeError  — type mismatches, undefined variables, etc.

All errors carry a line number and produce the spec's single-line diagnostic
format:  Error on line N: message
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceLocation:
    """Position in source code for error reporting."""

    line: int
    column: int = 0

    def __str__(self) -> str:
        return f"line {self.line}"


class BareError(Exception):
    """Base class for all BARE errors."""

    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        self.message = message
        self.location = location
        super().__init__(self.format())

    def format(self) -> str:
        """Format as the spec's single-line diagnostic."""
        if self.location:
            return f"Error on line {self.location.line}: {self.message}"
        return f"Error: {self.message}"


class BareLexerError(BareError):
    """Error during tokenization (invalid characters, unterminated strings)."""

    pass


class BareParseError(BareError):
    """Error during parsing (syntax violations)."""

    pass


class BareRuntimeError(BareError):
    """Error during execution (type mismatches, undefined variables, etc.)."""

    pass
