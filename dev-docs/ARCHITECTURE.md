# BARE Architecture

This documents how the implementation is actually put together, as a companion
to [BARE_language_spec.md](BARE_language_spec.md) (the language design) and
[BARE_ide_plan.md](BARE_ide_plan.md) (the original phase plan). Where this
file and the plan disagree on a detail, this file describes what was actually
built — the plan was written before implementation and a few things
(directory names, exact signal shapes) shifted during the six phases.

## Two packages, one process

```
src/bare_core/     Lexer, parser, tree-walking interpreter. No PyQt6 import
                    anywhere in this package — it is pure Python and fully
                    unit-testable without a display.
src/bare_ide/       PyQt6 IDE. Imports bare_core; bare_core never imports
                    bare_ide. This one-way dependency is what makes bare_core
                    testable headless and, in principle, reusable outside
                    the IDE — even though BARE the *language* is IDE-locked
                    by design (no distributed CLI interpreter).
```

## bare_core: the interpreter pipeline

```
source text --> Lexer --> tokens --> Parser --> Program (AST) --> Interpreter
                (lexer.py)          (parser.py)                   (interpreter.py)
```

- **`tokens.py`** — `TokenType` enum, `Token` dataclass, `KEYWORDS` dict.
- **`lexer.py`** — hand-written scanner. No indentation tracking (BARE uses
  `end` keywords, not significant whitespace); emits `NEWLINE` tokens to
  delimit statements.
- **`ast_nodes.py`** — one dataclass per grammar production. Every node
  carries a `line` for error reporting.
- **`parser.py`** — recursive-descent, single-error model (raises
  `BareParseError` on the first problem rather than collecting a list).
  The parser's own call stack *is* the block stack — there's no explicit
  stack data structure for tracking `if`/`while`/`sub` nesting.
- **`environment.py`** — `Environment` holds a flat `variables: dict`. A sub
  call gets a brand-new `Environment` with **no parent link** — this is the
  spec's strictest rule (§5.2): subs cannot see or modify globals. There is
  no scope chain to walk anywhere in this codebase.
- **`builtins.py`** — `BUILTINS: Dict[str, Callable]`, plus `_bare_repr()`,
  the single source of truth for how a BARE value renders as text (used by
  `print` and `str()`). Note this is deliberately *unquoted* for strings —
  the IDE's Variable Watch panel (`debug_panel.py`) has its own `_watch_repr()`
  that quotes strings instead, because a debugger and a `print` statement
  have different, both-correct, conventions.
- **`interpreter.py`** — tree-walking `Interpreter`. Three callbacks make
  this class embeddable in a GUI without it knowing anything about Qt:
  - `output_callback(str)` — called on every `print`.
  - `input_callback(str) -> str` — called on every `input()`, receives the
    prompt, must return the typed value.
  - `step_callback(line, env)` — called before *every* statement. Built in
    Phase 1 for the IDE's future step-debugger, and indeed unused until
    Phase 5, at which point `debug_thread.py` uses it verbatim with no
    changes to `interpreter.py` needed.
  - `self.cancelled` — a plain bool, checked between statements
    (`_check_cancelled`). Setting it from another thread and letting the
    interpreter notice it on its next check is the entire cooperative-
    cancellation mechanism; there is no lock, because a bool read/write is
    already atomic enough for this "eventually stops" use case.

## bare_ide: component map

```
BareIDEMainWindow (main_window.py)
├── EditorPane (editor.py)            — QPlainTextEdit + gutter
│   ├── BareHighlighter (syntax.py)   — QSyntaxHighlighter, per-token regex rules
│   └── block_structure.py           — compute_scope_boxes(): pure function,
│                                       no Qt types, feeds EditorPane's
│                                       ExtraSelections
├── ConsolePane (terminal.py)         — output + inline input() field
├── VariableWatchPane (debug_panel.py)— QDockWidget, Name/Value table
├── InterpreterWorker (debug_thread.py) — QThread, one instance per Run/Step
├── SettingsDialog (settings_dialog.py) — Preferences
├── SettingsManager (settings.py)     — JSON file under ~/.config/bare_ide/
└── ThemeManager (themes.py)          — 6 built-in UITheme instances + QSS
```

Nothing in `bare_ide` talks to `InterpreterWorker` internals except
`main_window.py` — `editor.py`, `terminal.py`, and `debug_panel.py` only
know about plain Python values (line numbers, strings, a variables dict).
`main_window.py` is the only file that imports `bare_core` directly (for
`Lexer`/`Parser`) and the only file that imports `debug_thread`.

## Execution model: why a background thread

A BARE program can contain `while true ... end`. Phases 1–3 ran the
interpreter directly on the GUI thread, which meant an infinite loop froze
the whole IDE — acceptable during development, not acceptable to ship, since
this is exactly the kind of program a learning student writes by accident.

Phase 4 moved `Interpreter.execute()` onto `InterpreterWorker(QThread)`.
Lexing and parsing stay on the GUI thread deliberately — they're always
bounded (a finite token stream can only produce a finite AST), so there's no
freeze risk there, and keeping them synchronous means parse errors can be
reported immediately without any thread-hop.

```
GUI thread                          Worker thread (InterpreterWorker)
───────────                         ─────────────────────────────────
Lexer, Parser  (bounded, sync)
    │
    ▼
InterpreterWorker(program).start() ───────▶ Interpreter.execute(program)
    │                                            │
    │◀── output_ready(str) ──────────────────────┤ every print
    │◀── input_requested(str) ───────────────────┤ every input()
    │                                            │ (blocks on threading.Event)
provide_input(value) ──────────────────────▶     │ (event.set() unblocks it)
    │                                            │
    │◀── step_reached(line, vars) ───────────────┤ step mode / breakpoint
    │                                            │ (blocks on a 2nd Event)
resume(step_mode) ─────────────────────────▶     │
    │                                            │
    │◀── error_occurred / stopped ────────────────┤ terminal states
    │◀── execution_finished ─────────────────────┤ always emitted last
```

Two `threading.Event`s bridge the worker back to the GUI thread — one for
`input()`, one for step/breakpoint pauses. `stop()` sets *both*, so
cancelling while blocked on either one doesn't hang the worker. All the
Qt signals above cross threads via Qt's automatic queued-connection
mechanism (no manual `QMetaObject.invokeMethod` needed) since the emitting
object (`InterpreterWorker`) and the receiving slots (`BareIDEMainWindow`
methods) have different thread affinities.

`main_window._set_run_state("idle" | "running" | "paused")` is the single
place that derives all four Run/Stop/Step/Continue button-enabled states,
specifically to avoid the bug class where each signal handler independently
toggles buttons and two handlers disagree about the current state.

## Error and decoration model

Three independent "which line is decorated and how" pieces of state live on
`EditorPane`, each with its own `highlight_*` / `clear_*` pair, combined into
one `setExtraSelections()` call in `highlight_current_line()`:

| State | Set by | Visual | Cleared by |
|---|---|---|---|
| `_error_line` / `_error_type` | lex/parse error (GUI thread) or `error_occurred` signal (worker thread) | red squiggle (parse) or yellow background (runtime) | next edit, or next Run |
| `_step_line` | `step_reached` signal | green background | next edit, Run/Step/Continue, or finish |
| `_scope_boxes` | every `textChanged` | translucent per-depth background | recomputed on every edit, not really "cleared" |

Scope boxes are computed by a plain keyword-scan (`block_structure.py`), not
a full parse — deliberately, so a student's mid-edit syntax error (missing
`end`, dangling `if`) doesn't make the boxes disappear entirely, just
whichever specific block is unbalanced.

## Settings persistence

`SettingsManager` (`settings.py`) reads/writes a single JSON file at
`~/.config/bare_ide/settings.json`, structured as nested dataclasses
(`EditorSettings`, `ThemeSettings`, `WindowSettings`) under one `Settings`
root. `_dict_to_settings()` applies loaded JSON field-by-field with
`hasattr` checks rather than blindly deserializing, so adding a new setting
field (as Phase 6 did twice — `scope_boxes_enabled`, `first_run`) never
breaks loading an older settings file that predates it.
