"""Console Pane for BARE IDE.

Provides output display for print statements and error messages, plus
an inline input field for the `input()` builtin.

As of Phase 4, the interpreter runs on a background InterpreterWorker
thread (bare_ide.app.debug_thread), so the input bridge is a plain
non-blocking signal: show_input_prompt() reveals the field, and
input_submitted fires when the user presses Enter. main_window forwards
that value to the worker's threading.Event bridge. Nothing here blocks —
the worker thread is what's waiting, not the GUI.
"""

from PyQt6.QtWidgets import (
    QPlainTextEdit,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QToolButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat

from bare_ide.app.themes import UITheme
from bare_ide.app.settings import SettingsManager


class ConsolePane(QWidget):
    """Console output pane with a header label.

    Displays print output, error messages, and handles input() via an
    inline field (see show_input_prompt / input_submitted).
    """

    input_submitted = pyqtSignal(str)

    def __init__(
        self,
        parent=None,
        ui_theme: UITheme = None,
        settings: SettingsManager = None,
    ):
        super().__init__(parent)
        self.ui_theme = ui_theme
        self.settings = settings

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar: title label + clear button
        self.header = QFrame()
        self.header.setObjectName("panel_label")
        self.header.setFixedHeight(24)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(8, 0, 4, 0)
        header_layout.setSpacing(0)

        self.header_label = QLabel("CONSOLE")
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()

        self.clear_btn = QToolButton()
        self.clear_btn.setText("🗑")
        self.clear_btn.setToolTip("Clear Console (Ctrl+L)")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear)
        header_layout.addWidget(self.clear_btn)

        layout.addWidget(self.header)

        # Output area
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.output)

        # Inline input field — shown only while input() is awaiting a value
        self.input_line = QLineEdit()
        self.input_line.setVisible(False)
        self.input_line.returnPressed.connect(self._submit_input)
        layout.addWidget(self.input_line)

        self.apply_settings()

    def apply_settings(self):
        """Apply font settings to the console."""
        font_family = "JetBrains Mono"
        font_size = 12
        if self.settings:
            font_family = self.settings.settings.editor.font_family
            font_size = self.settings.settings.editor.font_size - 1

        font = QFont(font_family, font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.output.setFont(font)

    def apply_ui_theme(self, theme: UITheme):
        """Apply UI theme colors to the console."""
        self.ui_theme = theme
        font_family = "monospace"
        font_size = 12
        if self.settings:
            font_family = self.settings.settings.editor.font_family
            font_size = self.settings.settings.editor.font_size - 1

        self.output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.terminal_background};
                color: {theme.terminal_foreground};
                border: none;
                font-family: '{font_family}';
                font-size: {font_size}px;
            }}
        """)
        self.header.setStyleSheet(f"""
            QFrame#panel_label {{
                background-color: {theme.panel_background};
                border-bottom: 1px solid {theme.panel_border};
            }}
            QLabel {{
                color: {theme.editor_gutter_fg};
                font-size: 11px;
                font-weight: bold;
            }}
            QToolButton {{
                background-color: transparent;
                color: {theme.editor_gutter_fg};
                border: none;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 12px;
            }}
            QToolButton:hover {{
                background-color: {theme.browser_item_hover};
            }}
        """)
        self.input_line.setFont(self.output.font())
        self.input_line.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.input_background};
                color: {theme.terminal_foreground};
                border: 1px solid {theme.input_border};
                padding: 3px 6px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.input_focus_border};
            }}
        """)

    def clear(self):
        """Clear all console output."""
        self.output.clear()

    def append_output(self, text: str):
        """Append normal output text (from print statements)."""
        self.output.appendPlainText(text)

    def append_error(self, text: str):
        """Append error text in the error color."""
        color = self.ui_theme.error if self.ui_theme else "#f38ba8"
        self._append_colored(text, color)

    def append_info(self, text: str):
        """Append info text in the info/accent color."""
        color = self.ui_theme.info if self.ui_theme else "#89b4fa"
        self._append_colored(text, color)

    def _append_colored(self, text: str, color: str):
        """Append text as its own block (like append_output) and tint it.

        Uses the same appendPlainText() block-creation path as
        append_output() rather than manually inserting a trailing "\\n" —
        mixing the two produced a stray blank line between a colored line
        and the next plain one.
        """
        self.output.appendPlainText(text)
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.movePosition(
            QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor
        )
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.mergeCharFormat(fmt)

    def scroll_to_bottom(self):
        """Scroll the console to the bottom."""
        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # =========================================================================
    # Input — wired to the interpreter worker's input_requested signal
    # =========================================================================

    def show_input_prompt(self, prompt: str):
        """Display the prompt and reveal the input field.

        Non-blocking: the caller finds out about the submitted value via
        the input_submitted signal, not a return value. The worker thread
        is the one waiting (on a threading.Event), not this widget.
        """
        if prompt:
            self.append_info(prompt)
        self.scroll_to_bottom()
        self.input_line.setVisible(True)
        self.input_line.setFocus()

    def hide_input_prompt(self):
        """Hide the input field without submitting a value.

        Used when a run ends (error or Stop) while a prompt was pending.
        """
        self.input_line.clear()
        self.input_line.setVisible(False)

    def _submit_input(self):
        value = self.input_line.text()
        self.append_output(value)
        self.hide_input_prompt()
        self.input_submitted.emit(value)
