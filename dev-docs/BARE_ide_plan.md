# BARE IDE — Implementation Plan
### Fragillidae Software IDE Suite
**Companion document to BARE_language_spec.md**

---

## 1. Purpose & Constraint

BARE has no standalone interpreter binary distributed to students. The IDE **is** the runtime — there is no other way to execute a `.bare` file. This constraint shapes the whole architecture: the editor, the interpreter, and the console output all live in one PyQt6 process with no external process boundary.

---

## 2. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.11+ | Matches existing IDE Suite tooling |
| GUI | PyQt6 | Consistent with PEIDE, STEPS IDE, CLJDE |
| Editor widget | `QPlainTextEdit` + custom `QSyntaxHighlighter` | Avoids the QScintilla dependency; matches your existing "minimal JS, minimal external deps" preference |
| Interpreter | Hand-written recursive-descent parser + tree-walking evaluator | No parser-generator dependency; easiest to keep agent-readable and cold-startable |
| Packaging | PyInstaller | Single executable per platform (Linux/Windows/macOS via your existing build machines) |

No external libraries beyond PyQt6 are required for v1. This keeps the dependency footprint identical to your other IDE Suite projects.

---

## 3. Application Architecture

```
BareIDE (QMainWindow)
├── EditorPane (QPlainTextEdit + BareHighlighter)
├── ConsolePane (QPlainTextEdit, read-only, output + input prompt)
├── ToolBar
│   ├── Run
│   ├── Stop
│   ├── Step (enters step-debug mode)
│   └── New / Open / Save
├── StatusBar (line:col, run state)
└── (Phase 5+) VariableWatchPane (dock widget)
```

### Execution flow
1. Editor text → **Lexer** → token stream
2. Token stream → **Parser** → AST (list of statement nodes)
3. AST → **Interpreter** (tree-walking, single-threaded)
4. Interpreter writes to `ConsolePane` via a callback, not direct stdout — this is what lets the console live inside the GUI and lets step-mode pause between statements without blocking the Qt event loop.

Long-running programs (an infinite `while true`) run on a **QThread** separate from the GUI thread, with a `Stop` button that sets a cooperative cancellation flag checked between statements. This avoids freezing the IDE — a real risk for beginner code that accidentally loops forever.

---

## 4. Syntax Highlighting

Token categories mapped to the IDE Suite's amber/blue palette (adjust exact hex values to match your existing palette file):

| Token category | Example | Suggested color role |
|---|---|---|
| Keywords | `if`, `while`, `sub`, `end` | Blue (primary accent) |
| Builtins | `print`, `len`, `append` | Amber (secondary accent) |
| Strings | `"hello"` | Existing string color from suite |
| Numbers | `5`, `3.14` | Existing number color from suite |
| Comments | `# ...` | Muted/gray, italic |
| Literals | `true`, `false`, `null` | Distinct from keywords — these are values, and the highlighting should visually reinforce that they're not control-flow words |

Implemented as a single `QSyntaxHighlighter` subclass using regex rules per category — same pattern as your other IDE Suite editors, so this is largely portable code.

---

## 5. Error Display

Two-tier, matching the spec's "no try/catch" philosophy:

1. **Parse-time errors** (syntax mistakes): underline the offending line in the editor with a red squiggle (via `QTextEdit.ExtraSelection`), and print the message to the console pane. Do not attempt to run.
2. **Runtime errors** (during execution): halt the interpreter thread, highlight the currently-executing line in the editor (yellow background, not red — distinguishes "this is where it stopped" from "this is a syntax mistake"), and print the diagnostic line format from the spec (§7).

No stack traces are shown. A single line number and message is the entire error surface — consistent with keeping the error model as simple as the language itself.

---

## 6. Run / Step-Debug Model

### Run mode
Straight execution at full speed on the worker thread. Console fills as `print` statements execute. `input()` calls block the worker thread and pop focus to the console pane for the student to type a response.

### Step mode
This is the pedagogically important piece — letting a student watch execution one statement at a time.

- Interpreter execution loop checks a `step_mode` flag before each statement.
- If set, it emits a Qt signal with the current line number and pauses (via a `threading.Event`) until the student clicks **Step** again or **Continue**.
- The editor highlights the current line (a distinct color from both error highlights).
- The (Phase 5+) Variable Watch pane refreshes to show the current scope's variables and values after each step — this is arguably the single highest-value feature for teaching, since it makes the abstract idea of "state" visible and concrete.

### Breakpoints (Phase 5+)
Click in the editor's left gutter to toggle a breakpoint on a line. In Run mode, execution behaves like Step mode but only pauses at breakpoint lines, running freely otherwise.

---

## 7. File Format

- Extension: `.bare`
- Plain UTF-8 text, no binary header, no metadata — a `.bare` file should be readable in any text editor, reinforcing that the *language* is simple even if the IDE around it isn't.

---

## 8. Six-Phase Implementation Plan

Matching the phase structure you've used for PyRAD, so an agent can cold-start any phase independently.

### Phase 1 — Core Interpreter (no GUI)
- Lexer, parser, tree-walking evaluator as a standalone Python package
- All 11 keywords, all data types, all built-in functions from the spec
- Runnable via a throwaway CLI test harness (`python -m bare_core myfile.bare`) — **this harness is deleted before release**, since BARE must only run inside its IDE
- Unit tests covering every grammar rule and every example program in the spec

### Phase 2 — Minimal Editor Shell
- `QMainWindow` with `EditorPane`, `ConsolePane`, New/Open/Save
- Wire Phase 1 interpreter to a Run button; console shows `print` output
- No highlighting, no error decoration yet — just "it runs"

### Phase 3 — Syntax Highlighting & Error Display
- `BareHighlighter` implementation per §4
- Parse-time and runtime error decoration per §5
- `input()` wired to console pane with blocking behavior

### Phase 4 — Threading & Stop Control
- Move execution to `QThread` with cooperative cancellation
- Stop button, status bar run-state indicator
- Guard against GUI freeze on infinite loops (this is the phase most worth testing thoroughly with deliberately broken student-style programs)

### Phase 5 — Step-Debug & Variable Watch
- Step/Continue controls, current-line highlighting
- Breakpoint gutter
- Variable Watch dock widget, refreshed per step

### Phase 6 — Polish & Packaging
- Icon/branding integration (amber/blue family)
- PyInstaller build scripts for Linux/Windows/macOS
- Sample program library (FizzBuzz, factorial, list examples from the spec, plus a few more scaffolded exercises)
- First-run "about BARE" dialog explaining the keyword list — since the entire language fits on one screen, this is worth showing students on day one

---

## 9. Branding Notes

Suggested icon direction: something visually "stripped down" or "bare" — a minimalist line-drawing motif (a single bare tree branch, or a bare lightbulb filament) would fit both the name and the amber/blue palette, and reads clearly as distinct from FABLE's stack-O, LITHP's lisp motif, and CLASP's bracket design.

---

*Document version 1.0 — Fragillidae Software IDE Suite*
