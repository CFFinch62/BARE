"""BARE Environment — Scope and Variable Management.

Implements the scope rules from spec §5.2:
- Global scope: the top level of the program.
- Sub scope: each sub call gets its own local scope.
  Subs CANNOT see or modify global variables — no parent chain.
  This forces students to pass values as parameters and return them.
"""

from typing import Any, Dict, Optional

from .errors import BareRuntimeError, SourceLocation


class Environment:
    """Variable scope for the BARE interpreter.

    Each environment holds its own variables dict. Sub calls get a fresh
    Environment with no parent link, enforcing the spec's strict scoping.

    Attributes:
        variables: Dict mapping variable names to their current values.
    """

    def __init__(self) -> None:
        self.variables: Dict[str, Any] = {}

    def get(self, name: str, line: int) -> Any:
        """Look up a variable's value.

        Args:
            name: Variable name.
            line: Source line number for error reporting.

        Returns:
            The variable's current value.

        Raises:
            BareRuntimeError: If the variable is not defined in this scope.
        """
        if name in self.variables:
            return self.variables[name]
        raise BareRuntimeError(
            f"'{name}' is not defined",
            SourceLocation(line),
        )

    def set(self, name: str, value: Any) -> None:
        """Set a variable's value (creates it if it doesn't exist).

        Args:
            name: Variable name.
            value: The value to assign.
        """
        self.variables[name] = value

    def has(self, name: str) -> bool:
        """Check if a variable is defined in this scope."""
        return name in self.variables

    def get_all_variables(self) -> Dict[str, Any]:
        """Return a snapshot of all variables in this scope.

        Used by the Variable Watch panel in the IDE (Phase 5).
        """
        return dict(self.variables)
