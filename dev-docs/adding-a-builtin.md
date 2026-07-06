# Adding a new built-in function

Built-ins are ordinary callable names, not keywords — the grammar has no
idea how many there are, so adding one never touches the lexer, parser, or
`ast_nodes.py`. Everything happens in `bare_core/builtins.py`, plus a
handful of places that mirror the builtin list for humans (IDE highlighting,
docs). This was written while adding `time()`; use it as the checklist for
the next one.

## 1. Implement it in `src/bare_core/builtins.py`

- Write a `builtin_<name>(args: list, line: int) -> Any` function.
- Start with `_check_arg_count("<name>", args, N, line)` — every existing
  builtin validates its arity first, before looking at argument values.
  (`time()` takes 0 arguments, and `_check_arg_count` handles that the same
  as any other N.)
- Validate argument types by hand and raise `BareRuntimeError(msg,
  SourceLocation(line))` on mismatch, matching the phrasing other builtins
  use (e.g. `"'round' expects a number as its first argument, got {type}"`).
  Students see these messages directly, so keep them specific and free of
  Python jargon (no `TypeError`, no tracebacks).
- Add the function to the `BUILTINS` dict at the bottom of the file.
- Update the module docstring's function list at the top of the file.

If your builtin needs something the interpreter has but `builtins.py`
doesn't (e.g. an I/O callback), don't force it through this dict — follow
`input()`'s pattern instead: it's special-cased in
`interpreter.py::_call_function` *before* the `BUILTINS` dict lookup,
because it needs the IDE's `input_callback` hook. Anything that only needs
its arguments (math, strings, lists, the system clock) belongs in
`builtins.py` like everything else.

## 2. Add tests in `tests/unit/test_builtins.py`

Follow the existing per-builtin `class Test<Name>` pattern: one happy-path
test, one test per validation error (matching on a distinctive substring of
the error message), and a wrong-arg-count test. Run:

```
python -m pytest tests/unit/test_builtins.py -q
```

## 3. Update the places that list builtins for humans

None of these affect behavior — they're all "the list of builtins" spelled
out again for a human audience, and grep will find any spot missed:

```
grep -rn "random\|round" src/bare_ide docs README.md
```

As of this writing, that means:

- **`src/bare_ide/app/syntax.py`** — add the name to the `BUILTINS` regex so
  it gets syntax-highlighted in the editor.
- **`src/bare_ide/app/main_window.py`** — add it to the "About BARE" dialog's
  builtins line.
- **`docs/language-spec.md`** — add a row to the builtins table, plus a short
  example if the function's behavior isn't obvious from the row alone.
- **`docs/user-guide.md`** — add the name to the syntax-highlighting color
  table (§4).
- **`README.md`** — add it to the "Language quick reference" builtins line,
  and bump the count in `**N builtins:**`.

## 4. Verify end-to-end, not just unit tests

Run a real `.bare` file through the interpreter — unit tests exercise
`builtins.py` directly, but won't catch a grammar-level issue with calling
your function (e.g. zero-arg calls, if that's new for this builtin):

```
PYTHONPATH=src python3 -m bare_core path/to/script.bare
```

## What NOT to do

- Don't add a keyword. BARE's keyword list (`print`, `input`, `if`, `else`,
  `end`, `while`, `sub`, `return`, `and`, `or`, `not`) is fixed by the spec
  (§8 draws the line explicitly: keywords need grammar changes, builtins
  don't). If a feature seems to need new syntax rather than a callable,
  that's a language-design conversation, not a builtin addition.
- Don't skip the type/count validation "because the interpreter already
  checked." It hasn't — builtins are the boundary where BARE values (all
  dynamically typed) meet whatever Python operation you're wrapping.
- Don't return a raw Python type the rest of the interpreter doesn't
  expect. BARE only has four value types at runtime: `float` (all numbers,
  no separate int), `str`, `bool`, `list`, and `None` (BARE's `null`). Return
  one of those — e.g. `time()` returns `float`, not a Python `int` or a
  `datetime`.
