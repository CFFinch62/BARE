"""Variable Watch Panel for BARE IDE.

A dockable table of variable name -> value, refreshed on every
InterpreterWorker.step_reached signal while execution is paused (step mode
or a breakpoint). Shows whichever scope the interpreter handed the step
callback: sub locals if paused inside a sub call, globals otherwise —
bare_core's Environment has no parent chain for subs (spec §5.2), so
there's never more than one scope to show at once.
"""

from typing import Any, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QHeaderView, QTableWidget, QTableWidgetItem

from bare_ide.app.themes import UITheme


def _watch_repr(value: Any) -> str:
    """Format a value the way a debugger should: strings quoted, so they
    read as distinct from bare identifiers and numbers.

    bare_core's own _bare_repr (builtins.py) leaves strings unquoted to
    match `print` output — the right convention there, but not here.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return str(value)
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, list):
        return "[" + ", ".join(_watch_repr(v) for v in value) + "]"
    return str(value)


class VariableWatchPane(QDockWidget):
    """Dockable variable watch table."""

    def __init__(self, parent=None):
        super().__init__("Variable Watch", parent)
        self.setObjectName("variable_watch_dock")

        self.table = QTableWidget(0, 2, self)
        self.table.setHorizontalHeaderLabels(["Name", "Value"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setWidget(self.table)

    def update_variables(self, variables: Dict[str, Any]) -> None:
        """Replace the table contents with the given scope snapshot."""
        self.table.setRowCount(len(variables))
        for row, (name, value) in enumerate(variables.items()):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(_watch_repr(value)))

    def clear_variables(self) -> None:
        self.table.setRowCount(0)

    def apply_ui_theme(self, theme: UITheme) -> None:
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme.panel_background};
                color: {theme.foreground};
                gridline-color: {theme.panel_border};
                border: none;
            }}
            QHeaderView::section {{
                background-color: {theme.panel_background};
                color: {theme.editor_gutter_fg};
                border: none;
                border-bottom: 1px solid {theme.panel_border};
                padding: 4px;
                font-weight: bold;
            }}
        """)
