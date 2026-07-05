"""BARE Built-in Functions.

Seven built-in functions from spec §8. These are ordinary callable names,
not keywords, so this list can grow without touching the grammar.

    len(x)              — Length of a string or list
    append(list, v)     — Appends value, returns modified list
    input(prompt)       — Prints prompt, reads a line, returns string
    str(x)              — Converts any value to its string form
    num(x)              — Converts a string to a number
    random(min, max)    — Random integer in [min, max] inclusive
    round(x, decimals)  — Rounds x to the given number of decimal places
"""

import random as _random
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Callable, Dict, List, Optional

from .errors import BareRuntimeError, SourceLocation


def _bare_repr(value: Any) -> str:
    """Convert a BARE value to its display string.

    Used by both str() builtin and print statement.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        # Display integers without decimal point: 5.0 → "5"
        if value == int(value) and not (value != value):  # not NaN
            return str(int(value))
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        elements = ", ".join(_bare_repr(e) for e in value)
        return f"[{elements}]"
    return str(value)


def _check_arg_count(
    name: str, args: list, expected: int, line: int
) -> None:
    """Validate argument count for a builtin function."""
    if len(args) != expected:
        raise BareRuntimeError(
            f"'{name}' expects {expected} argument(s), got {len(args)}",
            SourceLocation(line),
        )


def builtin_len(args: list, line: int) -> float:
    """len(x) — Length of a string or list."""
    _check_arg_count("len", args, 1, line)
    val = args[0]
    if isinstance(val, (str, list)):
        return float(len(val))
    raise BareRuntimeError(
        f"'len' expects a string or list, got {type(val).__name__}",
        SourceLocation(line),
    )


def builtin_append(args: list, line: int) -> list:
    """append(list, value) — Appends value, returns the modified list."""
    _check_arg_count("append", args, 2, line)
    target = args[0]
    value = args[1]
    if not isinstance(target, list):
        raise BareRuntimeError(
            f"'append' expects a list as first argument, got {type(target).__name__}",
            SourceLocation(line),
        )
    target.append(value)
    return target


def builtin_str(args: list, line: int) -> str:
    """str(x) — Converts any value to its string form."""
    _check_arg_count("str", args, 1, line)
    return _bare_repr(args[0])


def builtin_num(args: list, line: int) -> float:
    """num(x) — Converts a string to a number."""
    _check_arg_count("num", args, 1, line)
    val = args[0]
    if isinstance(val, float):
        return val
    if isinstance(val, str):
        try:
            return float(val)
        except ValueError:
            raise BareRuntimeError(
                f"cannot convert '{val}' to a number",
                SourceLocation(line),
            )
    raise BareRuntimeError(
        f"'num' expects a string or number, got {type(val).__name__}",
        SourceLocation(line),
    )


def builtin_random(args: list, line: int) -> float:
    """random(min, max) — Random integer in [min, max] inclusive."""
    _check_arg_count("random", args, 2, line)
    lo, hi = args[0], args[1]
    if not (isinstance(lo, float) and isinstance(hi, float)):
        raise BareRuntimeError(
            "'random' expects two numbers",
            SourceLocation(line),
        )
    lo_int, hi_int = int(lo), int(hi)
    if lo_int > hi_int:
        raise BareRuntimeError(
            f"'random' min ({lo_int}) must be <= max ({hi_int})",
            SourceLocation(line),
        )
    return float(_random.randint(lo_int, hi_int))


def builtin_round(args: list, line: int) -> float:
    """round(x, decimals) — Rounds x to the given number of decimal places.

    Uses half-up rounding (2.5 -> 3, not Python's default banker's rounding)
    since that's what students expect from math class.
    """
    _check_arg_count("round", args, 2, line)
    val, decimals = args[0], args[1]
    if not isinstance(val, float):
        raise BareRuntimeError(
            f"'round' expects a number as its first argument, got {type(val).__name__}",
            SourceLocation(line),
        )
    if not isinstance(decimals, float) or decimals != int(decimals) or decimals < 0:
        raise BareRuntimeError(
            "'round' expects a non-negative whole number of decimal places",
            SourceLocation(line),
        )
    places = int(decimals)
    quantum = Decimal(1).scaleb(-places)
    return float(Decimal(str(val)).quantize(quantum, rounding=ROUND_HALF_UP))


# Registry of all built-in functions.
# The interpreter checks this dict before looking up user-defined subs.
# Each entry maps name → callable(args: list, line: int) → Any.
BUILTINS: Dict[str, Callable] = {
    "len": builtin_len,
    "append": builtin_append,
    "str": builtin_str,
    "num": builtin_num,
    "random": builtin_random,
    "round": builtin_round,
    # "input" is handled specially by the interpreter because it needs
    # the input_callback hook from the IDE. See interpreter.py.
}
