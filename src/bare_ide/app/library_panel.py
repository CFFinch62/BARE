"""Personal Library Panel for BARE IDE.

A dockable list of the subs the student has saved to their personal
library (~/.config/bare_ide/user_library.bare, see settings.get_config_dir
and main_window._load_library_program). Double-clicking an entry inserts a
ready-to-edit call template at the editor's cursor rather than pasting the
function's body — the body lives once in user_library.bare and is loaded
into the interpreter's global scope at Run time (debug_thread.py), so this
panel is a reference list, not a snippet clipboard.
"""

from pathlib import Path
from typing import Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDockWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from bare_core.ast_nodes import SubDefinition
from bare_core.errors import BareError
from bare_core.lexer import Lexer
from bare_core.parser import Parser
from bare_ide.app.themes import UITheme

PLACEHOLDER_TEXT = (
    "No functions saved yet — select a sub definition and choose "
    "Edit > Save to Library."
)


class LibraryPane(QDockWidget):
    """Dockable list of the student's saved library functions."""

    insert_requested = pyqtSignal(str)
    edit_requested = pyqtSignal()

    def __init__(self, library_path: Path, parent=None):
        super().__init__("My Library", parent)
        self.setObjectName("library_dock")
        self._library_path = library_path

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QLabel("  MY LIBRARY")
        self.header.setObjectName("panel_label")
        self.header.setFixedHeight(24)
        layout.addWidget(self.header)

        self.list_widget = QListWidget(container)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        self.edit_button = QPushButton("Edit Library File...", container)
        self.edit_button.setToolTip(
            "Open user_library.bare in the editor to rename, delete, or "
            "reorder saved functions"
        )
        self.edit_button.clicked.connect(self.edit_requested.emit)
        layout.addWidget(self.edit_button)

        self.setWidget(container)
        self.refresh()

    def refresh(self) -> None:
        """Re-read user_library.bare and rebuild the list.

        Called on show and after a "Save to Library" action completes.
        """
        self.list_widget.clear()
        signatures = self._load_signatures()
        if not signatures:
            placeholder = QListWidgetItem(PLACEHOLDER_TEXT)
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.list_widget.addItem(placeholder)
            return
        for name in sorted(signatures):
            item = QListWidgetItem(signatures[name])
            item.setData(Qt.ItemDataRole.UserRole, signatures[name])
            self.list_widget.addItem(item)

    def _load_signatures(self) -> Dict[str, str]:
        """Return {name: "name(params)"} for each sub in the library file."""
        if not self._library_path.exists():
            return {}
        source = self._library_path.read_text(encoding="utf-8")
        if not source.strip():
            return {}
        try:
            tokens = Lexer(source).tokenize()
            program = Parser(tokens).parse()
        except BareError:
            # A broken library is reported to the student when they hit
            # Run (main_window._load_library_program) — here, just show
            # nothing rather than crash the panel.
            return {}
        return {
            stmt.name: f"{stmt.name}({', '.join(stmt.params)})"
            for stmt in program.statements
            if isinstance(stmt, SubDefinition)
        }

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        call_template = item.data(Qt.ItemDataRole.UserRole)
        if call_template:
            self.insert_requested.emit(call_template)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.refresh()

    def apply_ui_theme(self, theme: UITheme) -> None:
        self.header.setStyleSheet(f"""
            QLabel {{
                background-color: {theme.panel_background};
                color: {theme.editor_gutter_fg};
                border-bottom: 1px solid {theme.panel_border};
                font-size: 11px;
                font-weight: bold;
                padding-left: 8px;
            }}
        """)
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme.panel_background};
                color: {theme.foreground};
                border: none;
            }}
            QListWidget::item:disabled {{
                color: {theme.editor_gutter_fg};
            }}
        """)
        self.edit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.panel_background};
                color: {theme.foreground};
                border: none;
                border-top: 1px solid {theme.panel_border};
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {theme.panel_border};
            }}
        """)
