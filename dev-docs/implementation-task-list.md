# BARE Implementation — Task Tracker

## Phase 1 — Core Interpreter (No GUI) ✅ COMPLETE

### Project Setup
- [x] Create `pyproject.toml`
- [x] Create `.gitignore`
- [x] Create `setup.sh` / `run.sh`
- [x] Create package `__init__.py` files

### Interpreter Core
- [x] `errors.py` — SourceLocation, BareError hierarchy, format_error
- [x] `tokens.py` — TokenType enum, Token dataclass, KEYWORDS dict
- [x] `lexer.py` — Lexer class (full tokenization)
- [x] `ast_nodes.py` — All AST node dataclasses
- [x] `parser.py` — Recursive-descent parser (full grammar)
- [x] `environment.py` — Scope/variable management
- [x] `builtins.py` — 6 built-in functions
- [x] `interpreter.py` — Tree-walking evaluator
- [x] `__main__.py` — Temporary CLI harness

### Tests — Phase 1
- [x] `conftest.py` — Shared fixtures
- [x] `test_lexer.py` — Lexer unit tests
- [x] `test_parser.py` — Parser unit tests
- [x] `test_interpreter.py` — Interpreter unit tests
- [x] `test_environment.py` — Environment unit tests
- [x] `test_builtins.py` — Builtins unit tests
- [x] `test_full_pipeline.py` — Integration tests (spec examples)
- [x] `test_error_reporting.py` — Error format tests
- [x] Fixture `.bare` files (fizzbuzz, factorial, lists, guessing_game)
- [x] All 215 tests pass ✓

### Example Programs
- [x] `fizzbuzz.bare`
- [x] `factorial.bare`
- [x] `lists.bare`
- [x] `guessing_game.bare`

---

## Phase 2 — Minimal Editor Shell ✅ COMPLETE
- [x] `bare_ide/__init__.py` + `main.py` — App entry point
- [x] `themes.py` — ThemeManager (6 themes, amber/blue accents)
- [x] `settings.py` — SettingsManager
- [x] `editor.py` — EditorPane with line numbers
- [x] `terminal.py` — ConsolePane (output only)
- [x] `main_window.py` — BareIDEMainWindow (Run, New, Open, Save)
- [x] IDE launches and runs programs ✓ (verified headless: fizzbuzz, runtime/parse
      errors, save/open roundtrip, theme switching, guessing_game.bare via a
      modal `QInputDialog` stand-in for `input()` — the console-embedded input
      field lands in Phase 3)

Also fixed along the way (blocking Phase 2 verification):
- `Interpreter.execute()` was unconditionally resetting `self.cancelled = False`,
  which defeated the cooperative-cancellation flag the Stop button (Phase 4)
  depends on and caused the existing `test_cancellation` unit test to hang
  forever instead of failing. Removed the reset.
- Added a minimal root `README.md` — `pyproject.toml` declares it as the
  package readme, so `pip install -e .` failed outright without it. Full
  README content is still a Phase 6 deliverable; this is just enough to
  unblock installs.

---

## Phase 3 — Syntax Highlighting & Error Display ✅ COMPLETE
- [x] `syntax.py` — BareHighlighter (keywords, builtins, strings, numbers,
      comments, boolean/null literals; theme-aware, rebuilds on theme switch)
- [x] Editor error decoration (red squiggle for parse/lexer errors, yellow
      full-width highlight for runtime errors — `EditorPane.highlight_error()`
      / `clear_error_highlights()`, cleared automatically on the next edit)
- [x] Console `input()` wiring — inline `QLineEdit` in `ConsolePane`, blocks
      the (still single-threaded) interpreter via a nested `QEventLoop`
      rather than a background thread; real threading arrives in Phase 4.
      Replaces the Phase 2 modal `QInputDialog` stand-in.
- [x] Highlighting and errors work visually ✓ (verified headless — token
      colors, squiggle/background decorations, error clears on edit — and
      on-screen via screenshot with a real runtime error)

---

## Phase 4 — Threading & Stop Control ✅ COMPLETE
- [x] `debug_thread.py` — InterpreterWorker (QThread). Lexing/parsing stay on
      the GUI thread (always bounded, can't hang); only `interpreter.execute()`
      — the only unbounded part — runs on the worker.
- [x] Stop button + run state management (toolbar + Run menu; Run/Stop
      enabled state flip correctly; status bar shows Running.../Stopping.../
      Stopped/Ready/Error on line N)
- [x] Input bridge (threading.Event) — `input()` blocks the worker thread
      (not the GUI) on a `threading.Event`; `stop()` also sets it so a
      cancel during a pending `input()` doesn't hang the worker forever.
      Replaces Phase 3's nested-QEventLoop console bridge (`ConsolePane`
      now exposes a plain non-blocking `show_input_prompt()` /
      `input_submitted` signal instead).
- [x] Infinite loop stoppable, GUI never freezes ✓ (verified headless: a
      `while true` loop was run, a QTimer kept ticking the whole time
      proving the GUI thread stayed live, then Stop cleanly terminated it;
      also confirmed on-screen via screenshots mid-loop and after Stop)

---

## Phase 5 — Step-Debug & Variable Watch ✅ COMPLETE
- [x] Step mode in debug_thread — `InterpreterWorker` reuses bare_core's
      existing `step_callback` hook (built in Phase 1 for exactly this) to
      pause on a second `threading.Event` whenever `step_mode` is on or the
      line is a breakpoint; emits `step_reached(line, variables)`.
      `stop()` also releases this event so cancelling while paused doesn't
      hang the worker.
- [x] `debug_panel.py` — `VariableWatchPane(QDockWidget)`, a Name/Value
      table refreshed on every pause. Values are quoted/formatted debugger-
      style (distinct from bare_core's unquoted `print`-style repr).
- [x] Step/Continue buttons (toolbar + Run menu, F10/F6), with a single
      `_set_run_state("idle"|"running"|"paused")` helper driving all four
      Run/Stop/Step/Continue enabled-states consistently.
- [x] Breakpoint gutter in editor — click the line-number margin to toggle
      a dot (`toggle_breakpoint`/`get_breakpoints`/`set_breakpoints`);
      `highlight_step_line()` decorates the paused-on line in a distinct
      green, separate from the error red/yellow from Phase 3.
- [x] Step mode + variable watch working ✓ (verified headless: breakpoint
      toggling, pausing inside a sub call with only the sub's local scope
      shown — global vars correctly excluded — Continue running to
      completion, cold-start Step advancing one statement at a time with
      the watch panel updating each pause, and Stop cleanly terminating a
      paused worker instead of hanging; confirmed on-screen via screenshot)

Also added: the Variable Watch dock auto-shows on the first pause and its
visibility stays in sync with a View menu toggle (QDockWidget.visibilityChanged
→ checkbox). `closeEvent` now stops and waits on any live worker thread
before closing, since Phase 4/5 introduced real background execution that
could otherwise be destroyed mid-run.

---

## Phase 6 — Polish & Packaging ✅ COMPLETE
- [x] `block_structure.py` — Scope box coloring. Line-based keyword scan
      (if/while/sub open, else splits, end closes) rather than a full
      parse, so a mid-edit syntax error only drops the box for *that*
      unbalanced block instead of all of them. Rendered as translucent
      per-depth `ExtraSelection`s in `editor.py`, toggleable via a new
      `EditorSettings.scope_boxes_enabled` field.
- [x] `settings_dialog.py` — Preferences dialog (theme, font, font size,
      tab width, word wrap, scope boxes toggle), wired to Edit menu
      (Ctrl+,). Emits `settings_applied` so `main_window` can refresh
      theme/editor/console without the dialog knowing about them.
- [x] About BARE dialog — now also shown automatically on first launch
      (`Settings.first_run`, cleared and persisted after showing), in
      addition to the existing Help menu entry.
- [x] PyInstaller build spec + scripts — `installer/bare_ide.spec` (kept
      out of `build/` deliberately: `.gitignore` already excludes that
      directory wholesale since PyInstaller writes its own intermediate
      output there) + `build_release.sh`. **Actually built and ran**:
      produced `dist/bare-ide`, a 57MB standalone ELF executable with no
      Python/PyQt6 install required; launched cleanly with no import
      errors and created a real, correctly-titled window on the display.
- [x] `README.md` — screenshot, quick reference, doc links, project layout.
- [x] `dev-docs/ARCHITECTURE.md` — component responsibilities, the
      lex/parse-on-GUI-thread vs. execute-on-worker-thread split, the
      three editor decoration layers, settings persistence.
- [x] `dev-docs/TESTING_STRATEGY.md` — the pyramid (215 automated
      `bare_core` tests, no automated `bare_ide` suite yet — documented as
      a real gap, not hidden), fixture patterns, how to run the suite.
- [x] Single executable builds ✓ (see PyInstaller item above)

Also added (beyond the original task list, at user request):
- [x] `docs/language-spec.md` — user-facing language reference (not the
      dev-facing `dev-docs/BARE_language_spec.md`): every keyword,
      operator, type, control-flow construct, builtin, and example,
      written for someone writing BARE programs rather than implementing
      the interpreter.
- [x] `docs/user-guide.md` — IDE usage guide: window tour, running/
      debugging programs, breakpoints, Variable Watch, scope boxes,
      Preferences/themes, keyboard shortcuts, troubleshooting.

Verification notes:
- All 215 `bare_core` tests still pass, untouched by this phase.
- Scope box computation, the settings toggle, and Preferences `_apply()`
  were verified headless (including an intentionally unbalanced block to
  confirm no crash).
- The first-run About dialog was verified two ways: the call sequence
  (show About → clear flag → persist) with the dialog mocked out, and the
  real modal on the actual display (confirmed it appears, dismisses, and
  persists `first_run: false`) — the `QT_QPA_PLATFORM=offscreen` test
  platform turned out to hang on nested modal-dialog + timer interaction,
  which is a known limitation of that platform plugin, not a bug in the
  app; verifying on the real display was what actually confirmed it works.
- The screenshot used in the README and user guide was captured by the
  user directly (via Shutter) rather than through this session's headless
  scripting, after several automated screenshot attempts ran into the
  same offscreen-platform/backgrounded-process friction described above.
