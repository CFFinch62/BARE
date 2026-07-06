"""Main Window for BARE IDE.

BareIDEMainWindow wires the file browser, tabbed editors, console, Variable
Watch dock, and bare_core interpreter pipeline together: New/Open/Save,
Run/Stop/Step/Continue, basic Edit operations, syntax highlighting, and
error/step line decoration. Multiple files can be open at once as editor
tabs (each its own EditorPane); Run/Step/Continue always act on the tab that
was current when the run started. Execution runs on a background
InterpreterWorker thread (Phase 4) so an infinite BARE loop never freezes
the GUI, and the same worker's step_reached signal (Phase 5) drives
breakpoints and the Variable Watch panel.
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QTabWidget,
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
from bare_ide.app.file_browser import FileBrowserWidget
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
        self._worker: Optional[InterpreterWorker] = None
        self._run_editor: Optional[EditorPane] = None
        self._run_had_issue = False

        self.setWindowTitle("BARE IDE")
        self._restore_window_state()

        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_connections()

        # Start with a single blank tab so there's always something to edit.
        # Deferred until here: creating a tab fires currentChanged, which
        # touches widgets (e.g. the status bar's cursor label) that don't
        # exist until the setup methods above have run.
        self._create_tab()

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

        # Main horizontal split: file browser on the left, editor/console on the right.
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.file_browser = FileBrowserWidget(settings=self.settings)
        self.file_browser.file_double_clicked.connect(self._open_path)
        self.file_browser.setVisible(self.settings.settings.window.file_browser_visible)
        self.main_splitter.addWidget(self.file_browser)

        self.splitter = QSplitter(Qt.Orientation.Vertical)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.splitter.addWidget(self.tabs)

        self.console = ConsolePane(settings=self.settings)
        self.splitter.addWidget(self.console)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setSizes(self.settings.settings.window.splitter_sizes)

        self.main_splitter.addWidget(self.splitter)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes(self.settings.settings.window.main_splitter_sizes)

        layout.addWidget(self.main_splitter)

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
        undo_action.triggered.connect(lambda: self._current_editor() and self._current_editor().undo())

        redo_action = edit_menu.addAction("&Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(lambda: self._current_editor() and self._current_editor().redo())

        edit_menu.addSeparator()

        cut_action = edit_menu.addAction("Cu&t")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(lambda: self._current_editor() and self._current_editor().cut())

        copy_action = edit_menu.addAction("&Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(lambda: self._current_editor() and self._current_editor().copy())

        paste_action = edit_menu.addAction("&Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(lambda: self._current_editor() and self._current_editor().paste())

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
        self.toggle_file_browser_action = view_menu.addAction("File &Browser")
        self.toggle_file_browser_action.setCheckable(True)
        self.toggle_file_browser_action.setChecked(self.file_browser.isVisible())
        self.toggle_file_browser_action.triggered.connect(self.file_browser.setVisible)

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
        self.console.input_submitted.connect(self._on_input_submitted)

    # =========================================================================
    # Tabs
    # =========================================================================

    def _current_editor(self) -> Optional[EditorPane]:
        """The EditorPane in the currently active tab, or None if no tabs are open."""
        return self.tabs.currentWidget()

    def _create_tab(
        self,
        file_path: Optional[str] = None,
        content: str = "",
        add_to_recent: bool = False,
    ) -> EditorPane:
        """Create a new tab holding a fresh EditorPane and make it current."""
        editor = EditorPane(settings=self.settings)
        editor.file_path = file_path
        if content:
            editor.setPlainText(content)
        editor.set_clean()
        editor.apply_ui_theme(self.theme_manager.current_theme)
        editor.file_modified.connect(lambda modified, ed=editor: self._on_editor_modified(ed, modified))
        editor.cursorPositionChanged.connect(self._on_cursor_position_changed)

        index = self.tabs.addTab(editor, self._tab_label(editor))
        self.tabs.setTabToolTip(index, file_path or "Untitled")
        self.tabs.setCurrentIndex(index)

        if add_to_recent and file_path:
            self.settings.add_recent_file(file_path)

        return editor

    def _tab_label(self, editor: EditorPane) -> str:
        name = Path(editor.file_path).name if editor.file_path else "Untitled"
        return f"{'*' if editor.is_modified else ''}{name}"

    def _update_tab_label(self, editor: EditorPane):
        index = self.tabs.indexOf(editor)
        if index != -1:
            self.tabs.setTabText(index, self._tab_label(editor))
            self.tabs.setTabToolTip(index, editor.file_path or "Untitled")

    def _on_editor_modified(self, editor: EditorPane, _modified: bool):
        self._update_tab_label(editor)
        if editor is self._current_editor():
            self._update_title()

    def _on_tab_changed(self, _index: int):
        self._update_title()
        self._on_cursor_position_changed()

    def _on_tab_close_requested(self, index: int):
        self._close_tab_at(index)

    def _close_tab_at(self, index: int) -> bool:
        """Close the tab at *index*, prompting to save unsaved changes first."""
        editor = self.tabs.widget(index)
        if editor is None:
            return False
        self.tabs.setCurrentIndex(index)
        if not self._confirm_discard_changes(editor):
            return False
        self.tabs.removeTab(index)
        editor.deleteLater()
        return True

    # =========================================================================
    # File Operations
    # =========================================================================

    def _confirm_discard_changes(self, editor: Optional[EditorPane] = None) -> bool:
        """Ask the user to save unsaved changes in *editor* (default: the
        current tab). Returns True if it's safe to proceed."""
        if editor is None:
            editor = self._current_editor()
        if editor is None or not editor.is_modified:
            return True

        # An untitled file with nothing but whitespace in it has nothing
        # worth saving — don't nag about it just because typing-then-deleting
        # flipped the modified flag.
        if editor.file_path is None and not editor.toPlainText().strip():
            return True

        name = Path(editor.file_path).name if editor.file_path else "Untitled"
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
            return self._save_editor(editor)
        return result == QMessageBox.StandardButton.Discard

    def _new_file(self):
        self._create_tab()

    def _close_file(self):
        """File > Close — closes the current tab."""
        index = self.tabs.currentIndex()
        if index != -1:
            self._close_tab_at(index)

    def _open_file(self):
        start_dir = str(Path.home())
        editor = self._current_editor()
        if editor is not None and editor.file_path:
            start_dir = str(Path(editor.file_path).parent)
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open File", start_dir, "BARE Files (*.bare);;All Files (*)"
        )
        if filepath:
            self._open_path(filepath)

    def _open_path(self, filepath: str, add_to_recent: bool = True) -> bool:
        """Open *filepath* in a new tab, or switch to its tab if already open."""
        target = Path(filepath).resolve()
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor.file_path and Path(editor.file_path).resolve() == target:
                self.tabs.setCurrentIndex(i)
                return True

        try:
            text = Path(filepath).read_text(encoding="utf-8")
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
            return False

        self._create_tab(file_path=filepath, content=text, add_to_recent=add_to_recent)
        return True

    def _open_library_file(self):
        """File > Open My Library / the My Library panel's Edit button.

        Opens user_library.bare directly in its own tab (or switches to it
        if already open) so a student can freely rename, delete, or reorder
        subs — not just save one at a time via Edit > Save Selection to
        Library. A normal Ctrl+S writes straight back to the library file.
        """
        if not self.library_path.exists():
            self.library_path.parent.mkdir(parents=True, exist_ok=True)
            self.library_path.write_text("", encoding="utf-8")
        self._open_path(str(self.library_path), add_to_recent=False)

    def _save_file(self) -> bool:
        return self._save_editor(self._current_editor())

    def _save_file_as(self) -> bool:
        return self._save_editor_as(self._current_editor())

    def _save_editor(self, editor: Optional[EditorPane]) -> bool:
        if editor is None:
            return False
        if editor.file_path is None:
            return self._save_editor_as(editor)
        try:
            Path(editor.file_path).write_text(editor.toPlainText(), encoding="utf-8")
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
            return False
        editor.set_clean()
        self._update_tab_label(editor)
        if editor is self._current_editor():
            self._update_title()
        if editor.file_path == str(self.library_path):
            self.library_panel.refresh()
        return True

    def _save_editor_as(self, editor: Optional[EditorPane]) -> bool:
        if editor is None:
            return False
        start_dir = str(Path(editor.file_path).parent) if editor.file_path else str(Path.home())
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save File As", start_dir, "BARE Files (*.bare);;All Files (*)"
        )
        if not filepath:
            return False
        if not filepath.endswith(".bare"):
            filepath += ".bare"
        editor.file_path = filepath
        saved = self._save_editor(editor)
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

        editor = self._current_editor()
        if editor is None:
            return

        source = editor.toPlainText()
        self.console.clear()
        editor.clear_error_highlights()
        editor.clear_step_highlight()
        self.debug_panel.clear_variables()
        self.run_state_label.setText("Running...")

        # Run/Step/Continue always act on the tab that was current when the
        # run started, even if the user switches tabs while paused.
        self._run_editor = editor

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
            self._run_editor = None
            return

        library_program, library_ok = None, True
        if editor.file_path != str(self.library_path):
            # Editing the library file itself and hitting Run already
            # executes its exact (possibly unsaved) content as `program`
            # above — preloading it too would just rerun stale on-disk
            # content a second time and could misattribute an error to
            # "your library" using the wrong (on-disk) line numbers.
            library_program, library_ok = self._load_library_program()
        if not library_ok:
            self._run_editor = None
            return

        self._run_had_issue = False
        self._worker = InterpreterWorker(
            program,
            breakpoints=editor.get_breakpoints(),
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
        editor = self._current_editor()
        if editor is None:
            return
        editor.insertPlainText(text)
        editor.setFocus()

    def _save_selection_to_library(self) -> None:
        """Handle Edit > Save Selection to Library.

        Requires the selection to be exactly one complete `sub...end`
        block, then find-or-appends it into user_library.bare by name
        (via extract_sub_blocks) so re-saving an edited sub overwrites the
        old copy instead of duplicating it.
        """
        editor = self._current_editor()
        if editor is None:
            return

        # QTextCursor.selectedText() uses U+2029 as its line separator
        # instead of '\n' — undo that before handing the text to the lexer.
        source = editor.textCursor().selectedText().replace(chr(0x2029), "\n")

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
        if self._run_editor is not None:
            self._run_editor.clear_step_highlight()
        self.debug_panel.clear_variables()
        self._set_run_state("running")
        self._worker.resume(step_mode)

    def _on_input_submitted(self, value: str):
        if self._worker is not None:
            self._worker.provide_input(value)

    def _on_step_reached(self, line: int, variables: dict):
        self._set_run_state("paused")
        self.run_state_label.setText(f"Paused at line {line}")
        if self._run_editor is not None:
            self._run_editor.highlight_step_line(line)
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
        if self._run_editor is not None:
            self._run_editor.clear_step_highlight()
        self.debug_panel.clear_variables()
        if not self._run_had_issue:
            self.run_state_label.setText("Ready")
        self._worker = None
        self._run_editor = None

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

        # Don't let the tab bound to a run/step session get closed out from
        # under the worker thread while it's still highlighting lines in it.
        self.tabs.setTabsClosable(is_idle)

    def _show_error(self, message: str, line: Optional[int], error_type: str):
        """Report an error (lex/parse-time on the GUI thread, or runtime
        from the worker thread) to the console, editor, and status bar."""
        self._run_had_issue = True
        self.console.append_error(message)
        if line and self._run_editor is not None:
            self._run_editor.highlight_error(line, error_type)
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
        for i in range(self.tabs.count()):
            self.tabs.widget(i).apply_ui_theme(theme)
        self.file_browser.apply_ui_theme(theme)
        self.console.apply_ui_theme(theme)
        self.debug_panel.apply_ui_theme(theme)
        self.help_panel.apply_ui_theme(theme)
        self.spec_panel.apply_ui_theme(theme)
        self.library_panel.apply_ui_theme(theme)

    # =========================================================================
    # Misc UI
    # =========================================================================

    def _update_title(self):
        editor = self._current_editor()
        name = Path(editor.file_path).name if (editor and editor.file_path) else "Untitled"
        dirty_marker = "*" if (editor and editor.is_modified) else ""
        self.setWindowTitle(f"{dirty_marker}{name} — BARE IDE")

    def _on_cursor_position_changed(self):
        editor = self._current_editor()
        if editor is None:
            self.cursor_label.setText("")
            return
        cursor = editor.textCursor()
        self.cursor_label.setText(f"Ln {cursor.blockNumber() + 1}, Col {cursor.columnNumber() + 1}")

    def _show_preferences(self):
        dialog = SettingsDialog(self.settings, self.theme_manager, self)
        dialog.settings_applied.connect(self._on_settings_applied)
        dialog.exec()

    def _on_settings_applied(self):
        """Refresh everything that reads settings/theme after Preferences
        changes them (font, tab width, scope boxes, theme, ...)."""
        self._apply_theme()
        for i in range(self.tabs.count()):
            self.tabs.widget(i).apply_settings()
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
            "<p><b>Builtins:</b> len, append, str, num, random, round, time, input</p>"
            "<p>Part of the Fragillidae Software Teaching Language Suite.</p>",
        )

    # =========================================================================
    # Window Lifecycle
    # =========================================================================

    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor.is_modified:
                self.tabs.setCurrentIndex(i)
                if not self._confirm_discard_changes(editor):
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
        ws.main_splitter_sizes = self.main_splitter.sizes()
        ws.file_browser_visible = self.file_browser.isVisible()
        self.settings.save()

        event.accept()
