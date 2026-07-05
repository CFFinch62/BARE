"""Main Window for BARE IDE.

BareIDEMainWindow wires the editor, console, Variable Watch dock, and
bare_core interpreter pipeline together: New/Open/Save, Run/Stop/Step/
Continue, basic Edit operations, syntax highlighting, and error/step line
decoration. Execution runs on a background InterpreterWorker thread
(Phase 4) so an infinite BARE loop never freezes the GUI, and the same
worker's step_reached signal (Phase 5) drives breakpoints and the
Variable Watch panel.
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QToolBar,
    QStatusBar,
    QLabel,
    QFileDialog,
    QMessageBox,
    QApplication,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence

from bare_core.ast_nodes import SubDefinition
from bare_core.lexer import Lexer
from bare_core.parser import Parser
from bare_core.errors import BareError, BareLexerError, BareParseError
from bare_core.lib_utils import extract_sub_blocks

from bare_ide.app.settings import SettingsManager, get_config_dir
from bare_ide.app.themes import ThemeManager, THEMES
from bare_ide.app.editor import EditorPane
from bare_ide.app.terminal import ConsolePane
from bare_ide.app.debug_thread import InterpreterWorker
from bare_ide.app.debug_panel import VariableWatchPane
from bare_ide.app.help_panel import HelpPane
from bare_ide.app.library_panel import LibraryPane
from bare_ide.app.settings_dialog import SettingsDialog


class BareIDEMainWindow(QMainWindow):
    """The BARE IDE main window."""

    def __init__(
        self,
        settings: SettingsManager,
        theme_manager: ThemeManager,
        docs_dir: Optional[Path] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.theme_manager = theme_manager
        self.docs_dir = docs_dir or (Path(__file__).resolve().parent.parent.parent.parent / "docs")
        self.library_path = get_config_dir() / "user_library.bare"
        self.file_path: Optional[str] = None
        self._worker: Optional[InterpreterWorker] = None
        self._run_had_issue = False

        self.setWindowTitle("BARE IDE")
        self._restore_window_state()

        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_connections()

        self._apply_theme()
        self._update_title()

    # =========================================================================
    # Setup
    # =========================================================================

    def _restore_window_state(self):
        ws = self.settings.settings.window
        self.resize(ws.width, ws.height)
        if ws.maximized:
            self.showMaximized()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Vertical)

        self.editor = EditorPane(settings=self.settings)
        self.splitter.addWidget(self.editor)

        self.console = ConsolePane(settings=self.settings)
        self.splitter.addWidget(self.console)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setSizes(self.settings.settings.window.splitter_sizes)

        layout.addWidget(self.splitter)

        # Variable Watch dock — hidden until a step/breakpoint pause happens,
        # or the user opens it manually via the View menu.
        self.debug_panel = VariableWatchPane(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.debug_panel)
        self.debug_panel.hide()

        # User Guide dock — tabbed with Variable Watch on the same side so
        # either can be pulled up without disturbing the editor/console
        # layout; both start hidden and are toggled from the View menu.
        self.help_panel = HelpPane(self.docs_dir, self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.help_panel)
        self.tabifyDockWidget(self.debug_panel, self.help_panel)
        self.help_panel.hide()

        # Language Spec dock — same tab group as User Guide/Variable Watch.
        self.spec_panel = HelpPane(
            self.docs_dir,
            self,
            title="Language Spec",
            home_doc="language-spec.md",
            object_name="language_spec_dock",
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.spec_panel)
        self.tabifyDockWidget(self.help_panel, self.spec_panel)
        self.spec_panel.hide()

        # My Library dock — same tab group; lists subs from the student's
        # personal user_library.bare (see _load_library_program).
        self.library_panel = LibraryPane(self.library_path, self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.library_panel)
        self.tabifyDockWidget(self.spec_panel, self.library_panel)
        self.library_panel.insert_requested.connect(self._insert_at_cursor)
        self.library_panel.edit_requested.connect(self._open_library_file)
        self.library_panel.hide()

    def _setup_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = file_menu.addAction("&New")
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)

        open_action = file_menu.addAction("&Open...")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)

        open_library_action = file_menu.addAction("Open My &Library")
        open_library_action.triggered.connect(self._open_library_file)

        file_menu.addSeparator()

        close_action = file_menu.addAction("&Close")
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self._close_file)

        file_menu.addSeparator()

        save_action = file_menu.addAction("&Save")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)

        save_as_action = file_menu.addAction("Save &As...")
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_file_as)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = edit_menu.addAction("&Undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(lambda: self.editor.undo())

        redo_action = edit_menu.addAction("&Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(lambda: self.editor.redo())

        edit_menu.addSeparator()

        cut_action = edit_menu.addAction("Cu&t")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(lambda: self.editor.cut())

        copy_action = edit_menu.addAction("&Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(lambda: self.editor.copy())

        paste_action = edit_menu.addAction("&Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(lambda: self.editor.paste())

        edit_menu.addSeparator()

        edit_menu.addSeparator()

        save_to_library_action = edit_menu.addAction("Save Selection to &Library")
        save_to_library_action.triggered.connect(self._save_selection_to_library)

        preferences_action = edit_menu.addAction("&Preferences...")
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self._show_preferences)

        # View menu (theme switching — full Preferences dialog lands in Phase 6)
        view_menu = menubar.addMenu("&View")
        theme_menu = view_menu.addMenu("&Theme")
        self.theme_actions = []
        for key, theme in THEMES.items():
            action = theme_menu.addAction(theme.name)
            action.setCheckable(True)
            action.setChecked(key == self.settings.settings.theme.ui_theme)
            action.triggered.connect(lambda checked, k=key: self._set_theme(k))
            self.theme_actions.append((key, action))

        view_menu.addSeparator()
        self.toggle_debug_panel_action = view_menu.addAction("&Variable Watch")
        self.toggle_debug_panel_action.setCheckable(True)
        self.toggle_debug_panel_action.setChecked(False)
        self.toggle_debug_panel_action.triggered.connect(self.debug_panel.setVisible)
        self.debug_panel.visibilityChanged.connect(self.toggle_debug_panel_action.setChecked)

        self.toggle_help_panel_action = view_menu.addAction("&User Guide")
        self.toggle_help_panel_action.setCheckable(True)
        self.toggle_help_panel_action.setChecked(False)
        self.toggle_help_panel_action.triggered.connect(self.help_panel.setVisible)
        self.help_panel.visibilityChanged.connect(self.toggle_help_panel_action.setChecked)

        self.toggle_spec_panel_action = view_menu.addAction("&Language Spec")
        self.toggle_spec_panel_action.setCheckable(True)
        self.toggle_spec_panel_action.setChecked(False)
        self.toggle_spec_panel_action.triggered.connect(self.spec_panel.setVisible)
        self.spec_panel.visibilityChanged.connect(self.toggle_spec_panel_action.setChecked)

        self.toggle_library_panel_action = view_menu.addAction("My &Library")
        self.toggle_library_panel_action.setCheckable(True)
        self.toggle_library_panel_action.setChecked(False)
        self.toggle_library_panel_action.triggered.connect(self.library_panel.setVisible)
        self.library_panel.visibilityChanged.connect(self.toggle_library_panel_action.setChecked)

        view_menu.addSeparator()
        clear_console_action = view_menu.addAction("&Clear Console")
        clear_console_action.setShortcut("Ctrl+L")
        clear_console_action.triggered.connect(self.console.clear)

        # Run menu
        run_menu = menubar.addMenu("&Run")
        self.run_action = run_menu.addAction("&Run")
        self.run_action.setShortcut("F5")
        self.run_action.triggered.connect(self._run_program)

        self.stop_action = run_menu.addAction("&Stop")
        self.stop_action.setShortcut("Shift+F5")
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self._stop_program)

        run_menu.addSeparator()

        self.step_action = run_menu.addAction("S&tep")
        self.step_action.setShortcut("F10")
        self.step_action.triggered.connect(self._step_program)

        self.continue_action = run_menu.addAction("&Continue")
        self.continue_action.setShortcut("F6")
        self.continue_action.setEnabled(False)
        self.continue_action.triggered.connect(self._continue_program)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = help_menu.addAction("&About BARE")
        about_action.triggered.connect(self._show_about)

    def _setup_toolbar(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)

        new_btn = self.toolbar.addAction("New")
        new_btn.setToolTip("New File (Ctrl+N)")
        new_btn.triggered.connect(self._new_file)

        open_btn = self.toolbar.addAction("Open")
        open_btn.setToolTip("Open File (Ctrl+O)")
        open_btn.triggered.connect(self._open_file)

        save_btn = self.toolbar.addAction("Save")
        save_btn.setToolTip("Save (Ctrl+S)")
        save_btn.triggered.connect(self._save_file)

        self.toolbar.addSeparator()

        self.run_btn = self.toolbar.addAction("Run")
        self.run_btn.setToolTip("Run (F5)")
        self.run_btn.triggered.connect(self._run_program)

        self.stop_btn = self.toolbar.addAction("Stop")
        self.stop_btn.setToolTip("Stop (Shift+F5)")
        self.stop_btn.setEnabled(False)
        self.stop_btn.triggered.connect(self._stop_program)

        self.toolbar.addSeparator()

        self.step_btn = self.toolbar.addAction("Step")
        self.step_btn.setToolTip("Step — pause on the next statement (F10)")
        self.step_btn.triggered.connect(self._step_program)

        self.continue_btn = self.toolbar.addAction("Continue")
        self.continue_btn.setToolTip("Continue — run to the next breakpoint (F6)")
        self.continue_btn.setEnabled(False)
        self.continue_btn.triggered.connect(self._continue_program)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.run_state_label = QLabel("Ready")
        self.statusbar.addWidget(self.run_state_label)

        self.cursor_label = QLabel("Ln 1, Col 1")
        self.statusbar.addPermanentWidget(self.cursor_label)

    def _setup_connections(self):
        self.editor.file_modified.connect(self._on_modified_changed)
        self.editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.console.input_submitted.connect(self._on_input_submitted)

    # =========================================================================
    # File Operations
    # =========================================================================

    def _confirm_discard_changes(self) -> bool:
        """Ask the user to save unsaved changes. Returns True if it's safe to proceed."""
        if not self.editor.is_modified:
            return True

        # An untitled file with nothing but whitespace in it has nothing
        # worth saving — don't nag about it just because typing-then-deleting
        # flipped the modified flag.
        if self.file_path is None and not self.editor.toPlainText().strip():
            return True

        name = Path(self.file_path).name if self.file_path else "Untitled"
        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            f'"{name}" has unsaved changes. Save before continuing?',
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if result == QMessageBox.StandardButton.Save:
            return self._save_file()
        return result == QMessageBox.StandardButton.Discard

    def _new_file(self):
        if not self._confirm_discard_changes():
            return
        self._reset_to_untitled()

    def _close_file(self):
        """File > Close. There are no tabs/multiple documents in this IDE,
        so closing the current file and starting a new one both land on
        the same blank, untitled state — but a distinct, explicitly-named
        Close action is still worth having on its own rather than relying
        on New to imply it.
        """
        if not self._confirm_discard_changes():
            return
        self._reset_to_untitled()

    def _reset_to_untitled(self):
        self.editor.clear()
        self.editor.set_clean()
        self.file_path = None
        self._update_title()

    def _load_file_into_editor(self, filepath: str, add_to_recent: bool = True) -> bool:
        try:
            text = Path(filepath).read_text(encoding="utf-8")
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
            return False
        self.editor.setPlainText(text)
        self.editor.set_clean()
        self.file_path = filepath
        if add_to_recent:
            self.settings.add_recent_file(filepath)
        self._update_title()
        return True

    def _open_file(self):
        if not self._confirm_discard_changes():
            return
        start_dir = str(Path(self.file_path).parent) if self.file_path else str(Path.home())
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open File", start_dir, "BARE Files (*.bare);;All Files (*)"
        )
        if not filepath:
            return
        self._load_file_into_editor(filepath)

    def _open_library_file(self):
        """File > Open My Library / the My Library panel's Edit button.

        Opens user_library.bare directly in the main editor so a student
        can freely rename, delete, or reorder subs — not just save one at
        a time via Edit > Save Selection to Library. A normal Ctrl+S
        writes straight back to the library file.
        """
        if not self._confirm_discard_changes():
            return
        if not self.library_path.exists():
            self.library_path.parent.mkdir(parents=True, exist_ok=True)
            self.library_path.write_text("", encoding="utf-8")
        self._load_file_into_editor(str(self.library_path), add_to_recent=False)

    def _save_file(self) -> bool:
        if self.file_path is None:
            return self._save_file_as()
        try:
            Path(self.file_path).write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
            return False
        self.editor.set_clean()
        self._update_title()
        if self.file_path == str(self.library_path):
            self.library_panel.refresh()
        return True

    def _save_file_as(self) -> bool:
        start_dir = str(Path(self.file_path).parent) if self.file_path else str(Path.home())
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save File As", start_dir, "BARE Files (*.bare);;All Files (*)"
        )
        if not filepath:
            return False
        if not filepath.endswith(".bare"):
            filepath += ".bare"
        self.file_path = filepath
        saved = self._save_file()
        if saved:
            self.settings.add_recent_file(filepath)
        return saved

    # =========================================================================
    # Run / Stop / Step / Continue
    # =========================================================================

    def _run_program(self):
        self._start_worker(step_mode=False)

    def _step_program(self):
        if self._worker is None:
            # Cold start in step mode: pause on the very first statement.
            self._start_worker(step_mode=True)
        else:
            # Already paused: release for exactly one more statement.
            self._resume(step_mode=True)

    def _continue_program(self):
        if self._worker is not None:
            self._resume(step_mode=False)

    def _stop_program(self):
        if self._worker is not None:
            self._worker.stop()
            self.run_state_label.setText("Stopping...")

    def _start_worker(self, step_mode: bool):
        if self._worker is not None:
            return  # already running; buttons are disabled but guard anyway

        source = self.editor.toPlainText()
        self.console.clear()
        self.editor.clear_error_highlights()
        self.editor.clear_step_highlight()
        self.debug_panel.clear_variables()
        self.run_state_label.setText("Running...")

        # Lexing/parsing are always bounded (can't loop forever), so it's
        # fine to do them on the GUI thread. Only interpreter.execute() —
        # which can run an unbounded `while true ... end` — goes on the
        # worker thread.
        try:
            tokens = Lexer(source).tokenize()
            program = Parser(tokens).parse()
        except BareError as e:
            line = e.location.line if e.location else None
            error_type = "parse" if isinstance(e, (BareLexerError, BareParseError)) else "runtime"
            self._show_error(e.format(), line, error_type)
            return

        library_program, library_ok = None, True
        if self.file_path != str(self.library_path):
            # Editing the library file itself and hitting Run already
            # executes its exact (possibly unsaved) content as `program`
            # above — preloading it too would just rerun stale on-disk
            # content a second time and could misattribute an error to
            # "your library" using the wrong (on-disk) line numbers.
            library_program, library_ok = self._load_library_program()
        if not library_ok:
            return

        self._run_had_issue = False
        self._worker = InterpreterWorker(
            program,
            breakpoints=self.editor.get_breakpoints(),
            step_mode=step_mode,
            library_program=library_program,
        )
        self._worker.output_ready.connect(self.console.append_output)
        self._worker.input_requested.connect(self.console.show_input_prompt)
        self._worker.step_reached.connect(self._on_step_reached)
        self._worker.error_occurred.connect(self._on_worker_error)
        self._worker.stopped.connect(self._on_worker_stopped)
        self._worker.execution_finished.connect(self._on_worker_finished)
        self._worker.finished.connect(self._worker.deleteLater)

        self._set_run_state("running")
        self._worker.start()

    def _load_library_program(self):
        """Lex/parse the student's personal library file, if any.

        Returns (program_or_None, ok); ok is False only if the library
        exists but fails to lex/parse, in which case an error has already
        been shown and the caller should abort the run.
        """
        if not self.library_path.exists():
            return None, True
        source = self.library_path.read_text(encoding="utf-8")
        if not source.strip():
            return None, True
        try:
            tokens = Lexer(source).tokenize()
            return Parser(tokens).parse(), True
        except BareError as e:
            error_type = "parse" if isinstance(e, (BareLexerError, BareParseError)) else "runtime"
            # No line number passed through: it refers to user_library.bare,
            # not the open file, so highlighting a line here would be wrong.
            self._show_error(f"In your library — {e.format()}", None, error_type)
            return None, False

    def _insert_at_cursor(self, text: str) -> None:
        """Handle LibraryPane.insert_requested — drop a call template in."""
        self.editor.insertPlainText(text)
        self.editor.setFocus()

    def _save_selection_to_library(self) -> None:
        """Handle Edit > Save Selection to Library.

        Requires the selection to be exactly one complete `sub...end`
        block, then find-or-appends it into user_library.bare by name
        (via extract_sub_blocks) so re-saving an edited sub overwrites the
        old copy instead of duplicating it.
        """
        # QTextCursor.selectedText() uses U+2029 as its line separator
        # instead of '\n' — undo that before handing the text to the lexer.
        source = self.editor.textCursor().selectedText().replace(chr(0x2029), "\n")

        program = None
        if source.strip():
            try:
                tokens = Lexer(source).tokenize()
                program = Parser(tokens).parse()
            except BareError:
                program = None

        subs = [s for s in (program.statements if program else []) if isinstance(s, SubDefinition)]
        if program is None or len(program.statements) != 1 or len(subs) != 1:
            QMessageBox.warning(
                self,
                "Save to Library",
                "Select exactly one complete sub definition (from 'sub' to its matching 'end').",
            )
            return

        sub_name = subs[0].name
        existing_source = (
            self.library_path.read_text(encoding="utf-8") if self.library_path.exists() else ""
        )
        blocks = extract_sub_blocks(existing_source)

        if sub_name in blocks:
            reply = QMessageBox.question(
                self,
                "Save to Library",
                f"'{sub_name}' already exists in your library. Overwrite it?",
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        blocks[sub_name] = source.strip("\n")
        new_source = "\n\n".join(blocks.values()) + "\n"

        self.library_path.parent.mkdir(parents=True, exist_ok=True)
        self.library_path.write_text(new_source, encoding="utf-8")
        self.library_panel.refresh()
        self.console.append_info(f"Saved '{sub_name}' to your library.")

    def _resume(self, step_mode: bool):
        self.editor.clear_step_highlight()
        self.debug_panel.clear_variables()
        self._set_run_state("running")
        self._worker.resume(step_mode)

    def _on_input_submitted(self, value: str):
        if self._worker is not None:
            self._worker.provide_input(value)

    def _on_step_reached(self, line: int, variables: dict):
        self._set_run_state("paused")
        self.run_state_label.setText(f"Paused at line {line}")
        self.editor.highlight_step_line(line)
        self.debug_panel.update_variables(variables)
        if not self.debug_panel.isVisible():
            self.debug_panel.show()

    def _on_worker_error(self, message: str, line, error_type: str):
        self._show_error(message, line, error_type)

    def _on_worker_stopped(self):
        self._run_had_issue = True
        self.console.append_info("Execution stopped.")
        self.run_state_label.setText("Stopped")

    def _on_worker_finished(self):
        self._set_run_state("idle")
        self.console.hide_input_prompt()
        self.console.scroll_to_bottom()
        self.editor.clear_step_highlight()
        self.debug_panel.clear_variables()
        if not self._run_had_issue:
            self.run_state_label.setText("Ready")
        self._worker = None

    def _set_run_state(self, state: str):
        """state: "idle" (nothing running), "running" (free-running, not
        paused), or "paused" (blocked at a breakpoint or step)."""
        is_idle = state == "idle"
        is_paused = state == "paused"
        is_active = state in ("running", "paused")

        self.run_btn.setEnabled(is_idle)
        self.run_action.setEnabled(is_idle)
        self.stop_btn.setEnabled(is_active)
        self.stop_action.setEnabled(is_active)
        self.step_btn.setEnabled(is_idle or is_paused)
        self.step_action.setEnabled(is_idle or is_paused)
        self.continue_btn.setEnabled(is_paused)
        self.continue_action.setEnabled(is_paused)

    def _show_error(self, message: str, line: Optional[int], error_type: str):
        """Report an error (lex/parse-time on the GUI thread, or runtime
        from the worker thread) to the console, editor, and status bar."""
        self._run_had_issue = True
        self.console.append_error(message)
        if line:
            self.editor.highlight_error(line, error_type)
        self.run_state_label.setText(f"Error on line {line}" if line else "Error")

    # =========================================================================
    # Theme
    # =========================================================================

    def _set_theme(self, key: str):
        self.theme_manager.set_theme(key)
        self._apply_theme()
        for k, action in self.theme_actions:
            action.setChecked(k == key)

    def _apply_theme(self):
        theme = self.theme_manager.current_theme
        QApplication.instance().setStyleSheet(self.theme_manager.get_current_stylesheet())
        self.editor.apply_ui_theme(theme)
        self.console.apply_ui_theme(theme)
        self.debug_panel.apply_ui_theme(theme)
        self.help_panel.apply_ui_theme(theme)
        self.spec_panel.apply_ui_theme(theme)
        self.library_panel.apply_ui_theme(theme)

    # =========================================================================
    # Misc UI
    # =========================================================================

    def _update_title(self):
        name = Path(self.file_path).name if self.file_path else "Untitled"
        dirty_marker = "*" if self.editor.is_modified else ""
        self.setWindowTitle(f"{dirty_marker}{name} — BARE IDE")

    def _on_modified_changed(self, _modified: bool):
        self._update_title()

    def _on_cursor_position_changed(self):
        cursor = self.editor.textCursor()
        self.cursor_label.setText(f"Ln {cursor.blockNumber() + 1}, Col {cursor.columnNumber() + 1}")

    def _show_preferences(self):
        dialog = SettingsDialog(self.settings, self.theme_manager, self)
        dialog.settings_applied.connect(self._on_settings_applied)
        dialog.exec()

    def _on_settings_applied(self):
        """Refresh everything that reads settings/theme after Preferences
        changes them (font, tab width, scope boxes, theme, ...)."""
        self._apply_theme()
        self.editor.apply_settings()
        self.console.apply_settings()
        for key, action in self.theme_actions:
            action.setChecked(key == self.settings.settings.theme.ui_theme)

    def _show_about(self):
        QMessageBox.about(
            self,
            "About BARE",
            "<h3>BARE</h3>"
            "<p><i>Barely Adequate Runtime Environment</i></p>"
            "<p>A minimal procedural teaching language — "
            "11 reserved words, one numeric type, one loop, one procedure.</p>"
            "<p><b>Keywords:</b> print, input, if, else, end, while, sub, "
            "return, and, or, not</p>"
            "<p><b>Builtins:</b> len, append, str, num, random, round, input</p>"
            "<p>Part of the Fragillidae Software Teaching Language Suite.</p>",
        )

    # =========================================================================
    # Window Lifecycle
    # =========================================================================

    def closeEvent(self, event):
        if not self._confirm_discard_changes():
            event.ignore()
            return

        if self._worker is not None:
            # The user closed the window instead of clicking Stop — cancel
            # and wait briefly rather than let Qt destroy a live QThread.
            self._worker.stop()
            self._worker.wait(2000)

        ws = self.settings.settings.window
        ws.maximized = self.isMaximized()
        if not ws.maximized:
            ws.width = self.width()
            ws.height = self.height()
        ws.splitter_sizes = self.splitter.sizes()
        self.settings.save()

        event.accept()
