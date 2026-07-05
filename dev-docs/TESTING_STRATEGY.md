# BARE Testing Strategy

## The pyramid: bare_core is fully tested, bare_ide is not (yet)

```
                    ▲
                   / \        Manual / headless-Qt verification
                  /   \       (done ad hoc per phase, not automated)
                 /-----\
                /       \     215 automated tests
               / bare_core\    unit + integration
              /_____________\
```

`bare_core` has no PyQt6 dependency, so it gets a real automated suite.
`bare_ide` currently does **not** — every IDE feature (Run/Stop/Step,
breakpoints, Variable Watch, syntax highlighting, scope boxes, Preferences,
theming) was verified during development with one-off headless scripts
(`QT_QPA_PLATFORM=offscreen`, driving `BareIDEMainWindow` directly and
asserting on its internal state) and on-screen screenshots, not with a
committed `pytest-qt` suite. That's a real gap, not a design choice — see
"Future work" below.

## Running the suite

```bash
source venv/bin/activate
python -m pytest tests/ -v                                    # everything
python -m pytest tests/unit/ -v                                # unit only
python -m pytest tests/integration/ -v                          # integration only
python -m pytest tests/ --cov=src/bare_core --cov-report=term-missing
```

215 tests, all in `bare_core`, run in well under a second — there's no I/O,
no GUI, no sleeping.

## Layout

```
tests/
├── conftest.py                    # lex / parse / run fixtures (see below)
├── unit/
│   ├── test_lexer.py              # every token type, comments, edge cases
│   ├── test_parser.py             # every grammar production, precedence
│   ├── test_interpreter.py        # arithmetic, coercion, control flow, subs
│   ├── test_environment.py        # scope isolation (the no-parent-chain rule)
│   └── test_builtins.py           # every builtin, argument-count errors
└── integration/
    ├── test_full_pipeline.py      # complete programs, source text → output
    └── test_error_reporting.py    # exact error message + line number format
```

The unit/integration split here is by *what's being exercised*
(one component vs. the full lex→parse→interpret pipeline), not by speed —
everything is fast enough that there was never a reason to skip a tier
locally.

## The three fixtures (conftest.py)

Almost every test uses one of three fixtures rather than constructing a
`Lexer`/`Parser`/`Interpreter` by hand:

```python
def test_something(run):
    output = run('print 1 + 1')
    assert output == ["2"]
```

- **`lex(source) -> List[Token]`** — for lexer unit tests.
- **`parse(source) -> Program`** — for parser unit tests; runs the lexer
  first since the parser needs tokens, but the test is asserting on AST
  shape, not tokens.
- **`run(source, input_values=None) -> List[str]`** — the one integration
  tests use most: runs the full pipeline and returns captured `print`
  output as a list of strings, one per call. `input_values` feeds a queue
  of canned responses to `input()` calls, in order; requesting more inputs
  than were provided returns `""` rather than raising, so a test with a
  wrong assumption about how many `input()` calls happen fails on its
  *assertion*, not with a confusing fixture-level error.

## What each layer is actually asserting

- **Lexer tests** assert token *sequences* — type, value, line/column —
  including deliberately malformed input (unterminated strings, invalid
  characters) to pin down the exact `BareLexerError` raised.
- **Parser tests** assert AST *shape* (which dataclass, which fields) for
  every grammar production, plus operator precedence via expressions like
  `1 + 2 * 3` and checking the tree nests the multiplication inside the
  addition, not the reverse.
- **Interpreter tests** assert *behavior*: given this source, this output.
  This is where the language semantics actually live — truthiness (`0` and
  `""` are truthy), type coercion rules (`"x" + 5` works, `"x" - 5`
  doesn't), scope isolation (a sub can't read a global by name).
- **Integration tests** run the example programs from the spec
  (`examples/*.bare`) end to end and check output byte-for-byte, plus a
  dedicated error-reporting suite that checks the *exact* diagnostic string
  (`"Error on line 7: cannot add string and boolean"`) — the format itself
  is part of the spec (§7), not an implementation detail, so it's tested
  as a first-class assertion rather than just "does this raise."

## Adding a test for a new language feature

1. Lexer test first if it introduces a new token.
2. Parser test for the new grammar production / AST node.
3. Interpreter test(s) for behavior, including at least one error-path test
   if the feature can fail at runtime.
4. If it's substantial enough to appear in `dev-docs/BARE_language_spec.md`
   §10's example programs, add an integration test using the `run` fixture
   with a realistic multi-line program, not just a one-liner.

## Future work: testing bare_ide

If `bare_ide` gets an automated suite, `pytest-qt` (`qtbot` fixture) is the
natural fit — it already speaks `QThread` and Qt signals, which is most of
what `InterpreterWorker` and `main_window.py`'s Run/Stop/Step/Continue logic
is. The manual verification scripts written during Phases 2–6 (constructing
a `BareIDEMainWindow` under `QT_QPA_PLATFORM=offscreen`, driving it via its
`_run_program`/`_step_program`/etc. methods, and asserting on
`editor._step_line`, `debug_panel.table`, button `isEnabled()` state) are a
reasonable starting point to convert into a committed suite rather than
one-off throwaway scripts.
