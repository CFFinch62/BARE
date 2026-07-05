# BARE (Barely Adequate Runtime Environment) — Implementation Plan

## Background

BARE is a minimal procedural teaching language with 11 reserved words, a single numeric type, one loop construct, and one procedure construct. It is part of the Fragillidae Software IDE Suite alongside Steps, Plain, and Forge. BARE is **IDE-locked** — there is no standalone interpreter; the editor, interpreter, and console all live in one PyQt6 process.

This plan is derived from two spec documents:
- [BARE_language_spec.md](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/BARE_language_spec.md) — Grammar, semantics, builtins, error model
- [BARE_ide_plan.md](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/BARE_ide_plan.md) — Six-phase architecture and IDE design

The project structure is modeled after the sibling projects, particularly:
- **STEPSv2** (Python interpreter + PyQt6 IDE — closest analog)
- **PLAIN** (Go interpreter + PyQt6 IDE)
- **FORGE** (C interpreter + PyQt6 IDE)

---

## User Review Required

> [!IMPORTANT]
> **Project layout decision**: The plan below proposes a `src/bare_core/` + `src/bare_ide/` split matching the STEPS `src/steps/` + `src/steps_ide/` pattern. Both packages ship in one repo, one `pyproject.toml`, one PyInstaller build. Confirm this matches your intent.

> [!IMPORTANT]
> **Python version**: The spec says Python 3.11+. STEPSv2 uses `>=3.10`. Should BARE target 3.11+ as the spec states, or match STEPS at 3.10+?

> [!IMPORTANT]
> **Theme system**: Steps/Plain/Forge all share an identical theme architecture (Dark/Light/Grey/Solarized Light/Solarized Dark/High Contrast) with a `ThemeManager` class. BARE's spec calls for an "amber/blue palette." Should BARE use the same 6-theme system with BARE-specific accent colors, or a simplified subset?

---

## Open Questions

> [!NOTE]
> **`input()` as keyword vs builtin**: The spec lists `input` in both the 11 reserved words (§2) and the builtin functions table (§8). The grammar has no `input_stmt` production — it's parsed as a `call_stmt`. Should `input` be treated purely as a builtin function (removing it from the reserved word list), or does it need keyword-level syntax highlighting while still being callable? The STEPS project handles `input` as a keyword. I'll default to: **highlight as keyword, implement as builtin** unless you say otherwise.

> [!NOTE]
> **`print` as keyword vs builtin**: Similar to `input`, `print` appears in the reserved words and has a grammar production (`print_stmt`). The spec treats it as a statement keyword (`print expression`), not a function call (`print(expression)`). This is clear — `print` is a keyword with statement-level syntax. Just confirming.

---

## Proposed Project Structure

```
BARE/
├── BARE_language_spec.md          # [EXISTS] Language specification
├── BARE_ide_plan.md               # [EXISTS] IDE plan
├── icons/                         # [EXISTS] SVG icons
├── pyproject.toml                 # [NEW] Project config (hatchling build)
├── setup.sh                       # [NEW] Dev environment setup
├── setup.bat                      # [NEW] Windows dev setup
├── run.sh                         # [NEW] Dev launcher (Linux/macOS)
├── run.bat                        # [NEW] Dev launcher (Windows)
├── README.md                      # [NEW] Project README
├── .gitignore                     # [NEW]
├── images/                        # [NEW] App icons (PNG exports from SVG)
├── src/
│   ├── bare_core/                 # [NEW] Interpreter package
│   │   ├── __init__.py
│   │   ├── __main__.py            # Temp CLI harness (deleted before release)
│   │   ├── tokens.py              # TokenType enum + Token dataclass
│   │   ├── lexer.py               # Lexer class
│   │   ├── ast_nodes.py           # AST node dataclasses
│   │   ├── parser.py              # Recursive-descent parser
│   │   ├── interpreter.py         # Tree-walking evaluator
│   │   ├── environment.py         # Scope/variable management
│   │   ├── builtins.py            # len, append, str, num, random, input
│   │   └── errors.py              # BareError, SourceLocation, error formatting
│   └── bare_ide/                  # [NEW] IDE package
│       ├── __init__.py
│       ├── main.py                # QApplication entry point
│       └── app/
│           ├── __init__.py
│           ├── main_window.py     # BareIDEMainWindow (QMainWindow)
│           ├── editor.py          # EditorPane (QPlainTextEdit + gutter)
│           ├── syntax.py          # BareHighlighter (QSyntaxHighlighter)
│           ├── terminal.py        # ConsolePane (output + input)
│           ├── debug_panel.py     # Variable Watch dock (Phase 5)
│           ├── debug_thread.py    # Worker thread + step/stop control
│           ├── settings.py        # SettingsManager (QSettings wrapper)
│           ├── settings_dialog.py # Preferences dialog
│           ├── themes.py          # ThemeManager (Dark/Light/etc.)
│           ├── block_structure.py # Scope box computation
│           └── widgets/           # Reusable widget components
│               └── __init__.py
├── tests/
│   ├── conftest.py                # Shared pytest fixtures
│   ├── unit/
│   │   ├── test_lexer.py
│   │   ├── test_parser.py
│   │   ├── test_interpreter.py
│   │   ├── test_environment.py
│   │   └── test_builtins.py
│   ├── integration/
│   │   ├── test_full_pipeline.py
│   │   └── test_error_reporting.py
│   └── fixtures/
│       ├── valid_programs/        # .bare test files
│       └── expected_outputs/      # Expected output per program
├── examples/                      # [NEW] Sample .bare programs
│   ├── fizzbuzz.bare
│   ├── factorial.bare
│   ├── lists.bare
│   └── guessing_game.bare
├── dev-docs/                      # [NEW] Developer documentation
│   ├── ARCHITECTURE.md
│   ├── TESTING_STRATEGY.md
│   └── change-logs/
├── build/                         # [NEW] Build scripts
│   └── bare_ide.spec              # PyInstaller spec
└── dist/                          # [NEW] Build output (gitignored)
```

---

## Proposed Changes

### Phase 1 — Core Interpreter (No GUI)

The interpreter is the foundation. Every other phase depends on it. This phase produces a fully-testable, standalone Python package with no GUI dependency.

---

#### [NEW] [pyproject.toml](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/pyproject.toml)

Hatchling-based project config modeled after [STEPSv2/pyproject.toml](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/pyproject.toml):
- `name = "bare-lang"`, `requires-python = ">=3.11"`
- Dependencies: `PyQt6>=6.5.0` (IDE optional-dep initially)
- Dev deps: `pytest`, `pytest-cov`, `black`, `isort`
- Entry points: `bare-ide = "bare_ide.main:main"`
- Hatch build packages: `["src/bare_core", "src/bare_ide"]`

---

#### [NEW] [errors.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/errors.py)

Error infrastructure following the spec's single-line diagnostic format (§7):
- `SourceLocation` dataclass: `line`, `column`, `file`
- `BareError(Exception)`: base with `message`, `location`
- `BareLexerError`, `BareParseError`, `BareRuntimeError` subclasses
- `format_error()` → `"Error on line 7: cannot add string and boolean"`

---

#### [NEW] [tokens.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/tokens.py)

Token definitions:
- `TokenType` enum: `PRINT`, `INPUT`, `IF`, `ELSE`, `END`, `WHILE`, `SUB`, `RETURN`, `AND`, `OR`, `NOT`, plus `NUMBER`, `STRING`, `IDENTIFIER`, `TRUE`, `FALSE`, `NULL`, all operators (`PLUS`, `MINUS`, `STAR`, `SLASH`, `PERCENT`, `CARET`, `EQ`, `EQEQ`, `BANGEQ`, `LT`, `GT`, `LTEQ`, `GTEQ`), `LPAREN`, `RPAREN`, `LBRACKET`, `RBRACKET`, `COMMA`, `NEWLINE`, `EOF`
- `Token` dataclass: `type`, `value`, `line`, `column`
- `KEYWORDS` dict mapping strings to `TokenType`

---

#### [NEW] [lexer.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/lexer.py)

Lexer class converting source text to token stream:
- **No indentation tracking** — BARE uses `end` keywords, not significant whitespace
- Handles: identifiers/keywords, number literals (int and decimal), string literals (double-quoted, with basic escape sequences `\n`, `\\`, `\"`), `# comments`, all operators including two-char (`==`, `!=`, `<=`, `>=`)
- Emits `NEWLINE` tokens to delimit statements
- Tracks line/column for every token (for error reporting and IDE highlighting)

---

#### [NEW] [ast_nodes.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/ast_nodes.py)

AST node hierarchy using dataclasses, modeled after [STEPSv2 ast_nodes.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/src/steps/ast_nodes.py):

| Category | Nodes |
|---|---|
| Base | `ASTNode`, `Expression`, `Statement` |
| Literals | `NumberLiteral`, `StringLiteral`, `BooleanLiteral`, `NullLiteral`, `ListLiteral` |
| Expressions | `BinaryOp`, `UnaryOp`, `Identifier`, `IndexAccess`, `FunctionCall` |
| Statements | `Assignment`, `IndexAssignment`, `PrintStatement`, `IfStatement`, `WhileStatement`, `SubDefinition`, `ReturnStatement`, `CallStatement` |
| Program | `Program` (list of statements) |

Every node carries a `line` attribute for error reporting.

---

#### [NEW] [parser.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/parser.py)

Hand-written recursive-descent parser implementing the EBNF grammar from spec §4:
- Operator precedence climbing (§6): `or` → `and` → `not` → comparison → additive → multiplicative → unary → power → primary
- Block parsing: `if...else...end`, `while...end`, `sub...end` tracked via implicit block stack (the parser's call stack *is* the block stack)
- Disambiguation: `identifier "(" ...` could be either `call_stmt` or an expression-level `FunctionCall` — the parser peeks ahead to decide
- Collects parse errors with line numbers; stops at first error (single-error model matching the spec's philosophy)

---

#### [NEW] [environment.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/environment.py)

Scope management per spec §5.2:
- `Environment` class with `variables: dict`, optional `parent: Environment`
- Global scope: top-level `Environment(parent=None)`
- Sub scope: `Environment(parent=None)` — **no access to globals** (spec: "Subs cannot see or modify global variables directly")
- `get(name)` → raises `BareRuntimeError` if not found (no parent chain for subs)
- `set(name, value)` → creates or updates in current scope
- `get_all_variables()` → dict snapshot for the Variable Watch panel (Phase 5)

---

#### [NEW] [builtins.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/builtins.py)

Six built-in functions from spec §8:

| Function | Implementation notes |
|---|---|
| `len(x)` | Works on strings and lists; runtime error otherwise |
| `append(list, value)` | Mutates list, returns it |
| `input(prompt)` | Calls an `input_callback` injected by the IDE (or `builtins.input` for CLI harness) |
| `str(x)` | Converts any BARE value to string representation |
| `num(x)` | Parses string to float; runtime error if not numeric |
| `random(min, max)` | Random int in [min, max] inclusive via `random.randint` |

Builtins are registered as a `BUILTINS` dict mapping name → callable, checked during function-call resolution in the interpreter.

---

#### [NEW] [interpreter.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/interpreter.py)

Tree-walking evaluator — the heart of the system:
- `Interpreter` class with `global_env`, `output_callback`, `input_callback`
- `execute(program: Program)` — walks statement list
- `evaluate(expr: Expression)` → value
- Type coercion rules from §5.7: `string + number` auto-converts number; all other mixed arithmetic is a runtime error
- Truthiness from §5.3: only `False` and `None` are falsy; `0` and `""` are truthy
- Sub calls: create fresh `Environment(parent=None)`, bind parameters, execute body, catch `ReturnValue` exception for early return
- **Cancellation flag**: `self._cancelled` checked between statements for cooperative stop (Phase 4 wires this to the GUI)
- **Step-mode hook**: `self._step_callback` called before each statement (Phase 5 wires this)

---

#### [NEW] [\_\_main\_\_.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_core/__main__.py)

Temporary CLI harness (`python -m bare_core myfile.bare`):
- Reads file, runs lexer → parser → interpreter pipeline
- Output via `print()`, input via `builtins.input()`
- **Deleted before release** per spec — BARE must only run inside its IDE

---

#### [NEW] Test Suite — Phase 1

Test structure matching [STEPSv2/tests](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/tests):

**Unit tests:**
- `test_lexer.py` — tokenization of every token type, comments, edge cases (empty source, unterminated strings, invalid characters)
- `test_parser.py` — every grammar production, operator precedence, error recovery
- `test_interpreter.py` — arithmetic, string concatenation, type coercion, truthiness, variable assignment, if/else/end, while/end, sub/return, recursion, lists
- `test_environment.py` — scope isolation, sub scope has no global access
- `test_builtins.py` — every builtin function, edge cases, error conditions

**Integration tests:**
- `test_full_pipeline.py` — complete programs from spec §10 (FizzBuzz, factorial, lists)
- `test_error_reporting.py` — parse errors and runtime errors produce correct line-number diagnostics

**Fixtures:**
- `valid_programs/` — `.bare` files for each spec example
- `expected_outputs/` — corresponding expected output files

---

### Phase 2 — Minimal Editor Shell

Wire the interpreter into a PyQt6 window. "It runs" is the bar — no frills yet.

---

#### [NEW] [main.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/main.py)

Entry point modeled after [PLAIN IDE main.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/PLAIN/plain_ide/main.py):
- Create `QApplication`, set app name/version/org
- Load `SettingsManager`, create `ThemeManager`, apply stylesheet
- Create and show `BareIDEMainWindow`

---

#### [NEW] [main_window.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/main_window.py)

`BareIDEMainWindow(QMainWindow)`:
- Central widget: `QSplitter` with `EditorPane` (left) and `ConsolePane` (bottom or right)
- Toolbar: Run, New, Open, Save
- Menu bar: File (New/Open/Save/Save As/Exit), Edit (Undo/Redo/Cut/Copy/Paste), Run (Run), Help (About)
- Status bar: line:col display, run state indicator
- File operations: `.bare` extension filter, track dirty state, prompt save on close
- Run action: read editor text → lexer → parser → interpreter, pipe output to console

---

#### [NEW] [editor.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/editor.py)

`EditorPane(QPlainTextEdit)`:
- Line number gutter (custom `QWidget` painted in `paintEvent`)
- Tab → 4 spaces auto-indent
- Current-line highlight (subtle background shade)
- Font: monospace system default (configurable later)
- Dirty state tracking (text changed signal)

---

#### [NEW] [terminal.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/terminal.py)

`ConsolePane(QPlainTextEdit)`:
- Read-only output area for `print` output and error messages
- Color-coded output: normal text vs error text (red)
- Clear on each Run
- `append_output(text)` method called by interpreter's output callback

---

#### [NEW] [settings.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/settings.py)

`SettingsManager` wrapping `QSettings`:
- Window geometry, splitter position
- Current theme selection
- Font size, tab width
- Recent files list
- Modeled after [STEPS settings.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/src/steps_ide/app/settings.py)

---

#### [NEW] [themes.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/themes.py)

`ThemeManager` class:
- 6 themes matching suite standard (Dark, Light, Grey, Solarized Light, Solarized Dark, High Contrast)
- BARE-specific accent colors: amber (secondary/builtins) and blue (primary/keywords)
- Syntax highlighting color roles per theme
- `get_current_stylesheet()` → full QSS string
- `scope_depth_colors` per theme (for Phase 5 scope boxes)
- Modeled after [FORGE themes.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/FORGE/forge_ide/app/themes.py)

---

### Phase 3 — Syntax Highlighting & Error Display

---

#### [NEW] [syntax.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/syntax.py)

`BareHighlighter(QSyntaxHighlighter)`:
- Regex-based rules per token category (matching spec §4 of the IDE plan):

| Category | Pattern | Color role |
|---|---|---|
| Keywords | `\b(print|input|if|else|end|while|sub|return|and|or|not)\b` | Blue (primary accent) |
| Builtins | `\b(len|append|str|num|random)\b` | Amber (secondary accent) |
| Strings | `"[^"]*"` | String color from theme |
| Numbers | `\b\d+(\.\d+)?\b` | Number color from theme |
| Comments | `#.*$` | Muted gray, italic |
| Boolean/Null literals | `\b(true|false|null)\b` | Distinct literal color |

---

#### [MODIFY] [editor.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/editor.py)

Add error decoration:
- **Parse-time errors**: red squiggle underline on offending line via `QTextEdit.ExtraSelection`
- **Runtime errors**: yellow background highlight on the line where execution stopped
- Methods: `highlight_error(line, error_type)`, `clear_error_highlights()`

---

#### [MODIFY] [terminal.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/terminal.py)

Wire `input()` to console:
- When interpreter calls `input(prompt)`, print prompt to console, switch console to editable mode
- Capture user input on Enter, return to interpreter
- Blocking behavior via `threading.Event` or Qt signal/slot bridge

---

### Phase 4 — Threading & Stop Control

---

#### [NEW] [debug_thread.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/debug_thread.py)

`InterpreterWorker(QThread)`:
- Runs interpreter on background thread
- Emits signals: `output_ready(str)`, `error_occurred(str, int)`, `input_requested(str)`, `execution_finished()`
- Cooperative cancellation: `self._cancelled` flag checked by interpreter between statements
- Input bridge: `threading.Event` that blocks worker thread while GUI collects input

---

#### [MODIFY] [main_window.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/main_window.py)

- Add **Stop** button to toolbar (disabled when not running)
- Status bar shows run state: "Ready" / "Running..." / "Stopped" / "Error on line N"
- Run button disabled during execution; Stop enabled
- Guard against GUI freeze on infinite loops

---

### Phase 5 — Step-Debug & Variable Watch

---

#### [MODIFY] [debug_thread.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/debug_thread.py)

Add step-mode support:
- `step_mode` flag, `threading.Event` for step/continue synchronization
- Emit `step_reached(line, variables_dict)` signal before each statement when in step mode
- Support breakpoint list: run freely, pause only at breakpoint lines

---

#### [NEW] [debug_panel.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/debug_panel.py)

`VariableWatchPane(QDockWidget)`:
- Table widget showing variable names and values
- Refreshed on each step signal
- Shows current scope variables (local if inside a sub, global if at top level)
- Values formatted as BARE would display them (strings quoted, lists shown as `[1, 2, 3]`)

---

#### [MODIFY] [main_window.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/main_window.py)

- Add **Step** and **Continue** buttons to toolbar
- Add Variable Watch dock widget (View menu toggle)
- Editor highlights current line during step mode (distinct color from error highlights)

---

#### [MODIFY] [editor.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/editor.py)

- Breakpoint gutter: click left margin to toggle breakpoint dot
- Current-step line highlight (e.g., light blue/green background)
- `set_breakpoints()`, `get_breakpoints()`, `highlight_step_line(line)`

---

### Phase 6 — Polish & Packaging

---

#### [NEW] [block_structure.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/block_structure.py)

Scope box coloring (matching the suite-wide feature from [feature_porting_checklist.md](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/memory/feature_porting_checklist.md)):
- BARE uses `end` keywords (like Beam), not indentation — needs keyword-pair-matching algorithm
- Match `if`/`end`, `while`/`end`, `sub`/`end` blocks; `else` splits the enclosing block
- Feed scope ranges to the editor's `paintEvent` for colored background rectangles

---

#### [NEW] [settings_dialog.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/src/bare_ide/app/settings_dialog.py)

Preferences dialog:
- Theme selector dropdown
- Font family/size
- Tab width
- Scope box coloring toggle + custom depth colors (4 swatches)

---

#### [NEW] Build & Packaging Scripts

- `build/bare_ide.spec` — PyInstaller spec for single-executable builds
- `build_release.sh` / `build_release.bat` — Automated build scripts
- `setup.sh` / `setup.bat` — Developer environment setup (venv + pip install)
- `run.sh` / `run.bat` — Development launcher scripts

---

#### [NEW] Example Programs

Sample `.bare` files for the bundled program library:
- `fizzbuzz.bare` — From spec §10
- `factorial.bare` — Recursion example from spec §10
- `lists.bare` — List operations from spec §10
- `guessing_game.bare` — Interactive `input()` + `random()` exercise
- `string_builder.bare` — String concatenation and type coercion demo
- `countdown.bare` — Simple while loop

---

#### [NEW] Developer Documentation

- `dev-docs/ARCHITECTURE.md` — Component responsibilities, data flow diagram
- `dev-docs/TESTING_STRATEGY.md` — Test pyramid, fixture patterns, running tests
- `dev-docs/change-logs/` — Changelog directory

---

#### [NEW] [README.md](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE/README.md)

Project README:
- BARE overview and design philosophy
- Setup instructions (development and user)
- Screenshot placeholder (added once IDE is functional)
- Language quick reference (11 keywords, 6 builtins)
- Link to spec documents

---

#### About Dialog

First-run "About BARE" dialog showing:
- The complete keyword list (all 11 fit on one screen)
- The 6 builtin functions
- BARE design philosophy one-liner
- Version and Fragillidae Software branding

---

## Verification Plan

### Automated Tests

```bash
# Run full test suite
cd /home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/BARE
python -m pytest tests/ -v --tb=short

# Run with coverage
python -m pytest tests/ --cov=src/bare_core --cov-report=term-missing

# Run only unit tests
python -m pytest tests/unit/ -v

# Run integration tests (spec example programs)
python -m pytest tests/integration/ -v
```

**Phase 1 gate**: All unit and integration tests pass. Every spec example program produces correct output via the CLI harness.

**Phase 2 gate**: IDE launches, opens/saves `.bare` files, Run button executes programs and shows output in console.

**Phase 3 gate**: Syntax highlighting renders correctly across all token categories. Parse errors show red squiggles; runtime errors show yellow highlight + console diagnostic.

**Phase 4 gate**: Infinite loop (`while true ... end`) can be stopped with the Stop button. GUI never freezes. `input()` works from the console pane.

**Phase 5 gate**: Step mode pauses at each statement, highlights current line, and Variable Watch shows correct variable values. Breakpoints toggle correctly and pause execution only at marked lines.

**Phase 6 gate**: PyInstaller produces a working single executable on Linux. Example programs run correctly. About dialog displays. Scope box coloring renders.

### Manual Verification

- Launch the IDE from source (`python -m bare_ide.main`) and visually confirm:
  - Theme rendering (test Dark and Light at minimum)
  - Syntax highlighting for all token categories
  - Error highlighting (parse-time red, runtime yellow)
  - Step-debug flow with Variable Watch
  - Scope box coloring on nested if/while/sub blocks
- Test with deliberately broken programs (unterminated strings, infinite loops, division by zero, out-of-range list access)
- Cross-platform: test the PyInstaller build on Linux (primary), and if available, Windows/macOS
