"""Shared test fixtures for the BARE test suite."""

import pytest
from typing import Any, List

import sys
import os

# Add src to path so bare_core can be imported
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from bare_core.lexer import Lexer
from bare_core.parser import Parser
from bare_core.interpreter import Interpreter
from bare_core.environment import Environment
from bare_core.tokens import Token


@pytest.fixture
def lex():
    """Create a lexer from source text."""
    def _lex(source: str) -> List[Token]:
        return Lexer(source).tokenize()
    return _lex


@pytest.fixture
def parse():
    """Parse source text into an AST Program node."""
    def _parse(source: str):
        tokens = Lexer(source).tokenize()
        return Parser(tokens).parse()
    return _parse


@pytest.fixture
def run():
    """Run a BARE program and capture output.

    Returns a function that takes source code and returns
    a list of output lines.
    """
    def _run(source: str, input_values: List[str] | None = None) -> List[str]:
        output: List[str] = []
        input_iter = iter(input_values or [])

        def output_callback(text: str) -> None:
            output.append(text)

        def input_callback(prompt: str) -> str:
            try:
                return next(input_iter)
            except StopIteration:
                return ""

        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        interpreter = Interpreter(
            output_callback=output_callback,
            input_callback=input_callback,
        )
        interpreter.execute(program)
        return output

    return _run


@pytest.fixture
def run_with_library():
    """Like `run`, but loads a library source's subs before running the
    main program — mirrors what the IDE does with user_library.bare.
    """
    def _run_with_library(library_source: str, source: str) -> List[str]:
        output: List[str] = []

        tokens = Lexer(library_source).tokenize()
        library_program = Parser(tokens).parse()

        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()

        interpreter = Interpreter(output_callback=output.append)
        interpreter.load_library(library_program)
        interpreter.execute(program)
        return output

    return _run_with_library
