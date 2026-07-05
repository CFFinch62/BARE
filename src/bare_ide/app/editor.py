"""Code Editor Widget for BARE IDE.

Provides a code editor with:
- Line number gutter with a click-to-toggle breakpoint dot
- Current line highlighting
- Tab-to-spaces auto-indent
- Dirty state tracking
- Theme-aware coloring
- Syntax highlighting (BareHighlighter)
- Error line decoration: red squiggle for parse errors, yellow background
  for runtime errors
- Step-line decoration: green background for the statement InterpreterWorker
  is paused on (Phase 5 step-debug)
- Scope box coloring: a translucent per-depth background behind nested
  if/while/sub bodies (Phase 6), toggleable in Preferences
"""

from typing import List, Optional, Set

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QRect, QSize, QPoint, pyqtSignal
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QTextFormat,
    QTextCharFormat,
    QFont,
    QTextCursor,
    QPaintEvent,
    QMouseEvent,
)

from bare_ide.app.themes import UITheme
from bare_ide.app.settings import SettingsManager
from bare_ide.app.syntax import BareHighlighter
from bare_ide.app.block_structure import ScopeBox, compute_scope_boxes


class LineNumberArea(QWidget):
    """Widget for displaying line numbers and breakpoint dots in the gutter."""

    def __init__(self, editor: "EditorPane"):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent):
        self.editor.line_number_area_paint_event(event)

    def mousePressEvent(self, event: QMouseEvent):
        line = self.editor.line_number_at_y(int(event.position().y()))
        if line is not None:
            self.editor.toggle_breakpoint(line)


class EditorPane(QPlainTextEdit):
    """Code editor with line numbers, current-line highlighting, and auto-indent.

    Signals:
        file_modified(bool): Emitted when the dirty state changes.
    """

    file_modified = pyqtSignal(bool)

    def __init__(
        self,
        parent=None,
        ui_theme: UITheme = None,
        settings: SettingsManager = None,
    ):
        super().__init__(parent)
        self.ui_theme = ui_theme
        self.settings = settings
        self.file_path = None
        self._modified = False
        self._error_line = None
        self._error_type = None
        self._step_line: Optional[int] = None
        self._breakpoints: Set[int] = set()
        self._scope_boxes: List[ScopeBox] = []

        # Create line number area
        self.line_number_area = LineNumberArea(self)

        # Syntax highlighting
        self.highlighter = BareHighlighter(self.document(), ui_theme)

        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.document().contentsChange.connect(self._on_contents_change)
        self.textChanged.connect(self.clear_error_highlights)
        self.textChanged.connect(self.clear_step_highlight)
        self.textChanged.connect(self._recompute_scope_boxes)

        # Initial setup
        self.update_line_number_area_width(0)
        self._recompute_scope_boxes()
        self.highlight_current_line()
        self.apply_settings()

    def apply_settings(self):
        """Apply editor settings (font, tab width, etc.)."""
        if self.settings:
            s = self.settings.settings.editor
            font = QFont(s.font_family, s.font_size)
            font.setStyleHint(QFont.StyleHint.Monospace)
            self.setFont(font)
            self.line_number_area.setFont(font)
            self.setTabStopDistance(
                s.tab_width * self.fontMetrics().horizontalAdvance(" ")
            )
            self.setLineWrapMode(
                QPlainTextEdit.LineWrapMode.WidgetWidth
                if s.word_wrap
                else QPlainTextEdit.LineWrapMode.NoWrap
            )
            self.line_number_area.setVisible(s.show_line_numbers)
            self.update_line_number_area_width(0)
        else:
            # Sensible defaults when no settings
            font = QFont("Monospace", 13)
            font.setStyleHint(QFont.StyleHint.Monospace)
            self.setFont(font)
            self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
        self.highlight_current_line()

    def apply_ui_theme(self, theme: UITheme):
        """Apply UI theme colors to the editor."""
        self.ui_theme = theme
        self.highlighter.set_theme(theme)
        font_family = "monospace"
        font_size = 13
        if self.settings:
            font_family = self.settings.settings.editor.font_family
            font_size = self.settings.settings.editor.font_size

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.editor_background};
                color: {theme.editor_foreground};
                border: none;
                font-family: '{font_family}';
                font-size: {font_size}px;
                selection-background-color: {theme.editor_selection};
            }}
        """)
        self.highlight_current_line()
        self.update()
        self.viewport().update()
        self.line_number_area.update()

    # =========================================================================
    # Line Number Area
    # =========================================================================

    def line_number_area_width(self) -> int:
        """Calculate the width needed for the line number gutter."""
        digits = len(str(max(1, self.blockCount())))
        digits = max(digits, 3)  # Minimum 3 digits wide
        space = 10 + self.fontMetrics().horizontalAdvance("9") * digits + 10
        return space

    def update_line_number_area_width(self, _):
        """Update the viewport margins to accommodate the line number area."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Scroll the line number area when the editor scrolls."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Resize the line number area when the editor resizes."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_at_y(self, y: int) -> Optional[int]:
        """Map a y-coordinate within the gutter to a 1-based line number.

        Mirrors the block-walking loop in line_number_area_paint_event so
        gutter clicks land on the line actually rendered at that position.
        """
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid():
            if top <= y < bottom:
                return block_number + 1
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
        return None

    def line_number_area_paint_event(self, event: QPaintEvent):
        """Paint line numbers and breakpoint dots in the gutter."""
        painter = QPainter(self.line_number_area)

        # Gutter background
        gutter_bg = "#181825"
        gutter_fg = "#6c7086"
        breakpoint_color = "#f38ba8"
        if self.ui_theme:
            gutter_bg = self.ui_theme.editor_gutter_bg
            gutter_fg = self.ui_theme.editor_gutter_fg
            breakpoint_color = self.ui_theme.error

        painter.fillRect(event.rect(), QColor(gutter_bg))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        # Current line number gets accent color
        current_block = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_number = block_number + 1

                if line_number in self._breakpoints:
                    painter.save()
                    painter.setBrush(QColor(breakpoint_color))
                    painter.setPen(Qt.PenStyle.NoPen)
                    radius = 4
                    cy = top + self.fontMetrics().height() // 2
                    painter.drawEllipse(QPoint(8, cy), radius, radius)
                    painter.restore()

                number = str(line_number)

                if block_number == current_block:
                    painter.setPen(
                        QColor(self.ui_theme.accent if self.ui_theme else "#89b4fa")
                    )
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                else:
                    painter.setPen(QColor(gutter_fg))
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 10,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

        painter.end()

    # =========================================================================
    # Breakpoints
    # =========================================================================

    def toggle_breakpoint(self, line: int):
        """Toggle a breakpoint on the given 1-based line number."""
        if line in self._breakpoints:
            self._breakpoints.discard(line)
        else:
            self._breakpoints.add(line)
        self.line_number_area.update()

    def get_breakpoints(self) -> Set[int]:
        return set(self._breakpoints)

    def set_breakpoints(self, lines) -> None:
        self._breakpoints = set(lines)
        self.line_number_area.update()

    # =========================================================================
    # Scope Box Coloring
    # =========================================================================

    def _recompute_scope_boxes(self):
        """Rescan the source for block nesting. Cheap line-based scan, not a
        full parse — safe to run on every keystroke (see block_structure.py)."""
        self._scope_boxes = compute_scope_boxes(self.toPlainText())
        self.highlight_current_line()

    def _build_scope_selections(self) -> List[QTextEdit.ExtraSelection]:
        """Build one translucent full-width ExtraSelection per scope box.

        Overlapping selections (nested blocks) stack additively since each
        is semi-transparent, so deeper nesting reads as a subtly deeper
        shade without any special-case blending logic.
        """
        if self.settings and not self.settings.settings.editor.scope_boxes_enabled:
            return []
        if not self._scope_boxes:
            return []

        colors = (
            self.ui_theme.scope_depth_colors
            if self.ui_theme
            else ["#f9c74f", "#577590", "#90be6d", "#9b5de5"]
        )
        doc = self.document()
        selections = []
        for box in self._scope_boxes:
            start_block = doc.findBlockByNumber(box.start_line - 1)
            end_block = doc.findBlockByNumber(box.end_line - 1)
            if not start_block.isValid() or not end_block.isValid():
                continue

            cursor = QTextCursor(start_block)
            cursor.setPosition(
                end_block.position() + end_block.length() - 1,
                QTextCursor.MoveMode.KeepAnchor,
            )

            selection = QTextEdit.ExtraSelection()
            color = QColor(colors[box.depth % len(colors)])
            color.setAlpha(26)
            selection.format.setBackground(color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = cursor
            selections.append(selection)

        return selections

    # =========================================================================
    # Current Line Highlighting
    # =========================================================================

    def highlight_current_line(self):
        """Highlight the line the cursor is on, plus any active step/error decoration."""
        extra_selections = []
        extra_selections.extend(self._build_scope_selections())

        if not self.isReadOnly():
            highlight_color = "#2a2a3c"
            if self.ui_theme:
                highlight_color = self.ui_theme.editor_line_highlight

            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(highlight_color))
            selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        step_selection = self._build_step_selection()
        if step_selection is not None:
            extra_selections.append(step_selection)

        error_selection = self._build_error_selection()
        if error_selection is not None:
            extra_selections.append(error_selection)

        self.setExtraSelections(extra_selections)

    # =========================================================================
    # Error Decoration
    # =========================================================================

    def highlight_error(self, line: int, error_type: str = "runtime"):
        """Decorate a source line with an error indicator.

        error_type: "parse" for a red squiggle under the line's text, or
        "runtime" for a full-width yellow background on the line where
        execution stopped.
        """
        self._error_line = line
        self._error_type = error_type
        self.highlight_current_line()

    def clear_error_highlights(self):
        """Remove any active error decoration."""
        if self._error_line is None:
            return
        self._error_line = None
        self._error_type = None
        self.highlight_current_line()

    def _build_error_selection(self):
        """Build the ExtraSelection for the active error line, if any."""
        if self._error_line is None:
            return None

        block = self.document().findBlockByNumber(self._error_line - 1)
        if not block.isValid():
            return None

        selection = QTextEdit.ExtraSelection()
        cursor = QTextCursor(block)

        if self._error_type == "parse":
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            color = QColor(self.ui_theme.error if self.ui_theme else "#f38ba8")
            selection.format.setUnderlineStyle(
                QTextCharFormat.UnderlineStyle.SpellCheckUnderline
            )
            selection.format.setUnderlineColor(color)
        else:
            cursor.clearSelection()
            bg = QColor(self.ui_theme.warning if self.ui_theme else "#f9e2af")
            bg.setAlpha(80)
            selection.format.setBackground(bg)
            selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )

        selection.cursor = cursor
        return selection

    # =========================================================================
    # Step Decoration (Phase 5 step-debug)
    # =========================================================================

    def highlight_step_line(self, line: int):
        """Mark the line InterpreterWorker is currently paused on.

        Moves the text cursor there too (and scrolls it into view), matching
        the "jump to current line" behavior of most step debuggers.
        """
        self._step_line = line
        block = self.document().findBlockByNumber(line - 1)
        if block.isValid():
            self.setTextCursor(QTextCursor(block))
            self.ensureCursorVisible()
        self.highlight_current_line()

    def clear_step_highlight(self):
        """Remove the step-line decoration, if any."""
        if self._step_line is None:
            return
        self._step_line = None
        self.highlight_current_line()

    def _build_step_selection(self):
        """Build the ExtraSelection for the paused-on line, if any."""
        if self._step_line is None:
            return None

        block = self.document().findBlockByNumber(self._step_line - 1)
        if not block.isValid():
            return None

        selection = QTextEdit.ExtraSelection()
        cursor = QTextCursor(block)
        cursor.clearSelection()

        bg = QColor(self.ui_theme.success if self.ui_theme else "#a6e3a1")
        bg.setAlpha(70)
        selection.format.setBackground(bg)
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)

        selection.cursor = cursor
        return selection

    # =========================================================================
    # Auto-Indent & Tab Handling
    # =========================================================================

    def keyPressEvent(self, event):
        """Handle Tab key (insert spaces) and auto-indent on Enter."""
        tab_width = 4
        if self.settings:
            tab_width = self.settings.settings.editor.tab_width

        if event.key() == Qt.Key.Key_Tab:
            # Insert spaces instead of tab
            self.insertPlainText(" " * tab_width)
            return

        if event.key() == Qt.Key.Key_Backtab:
            # Shift+Tab: remove up to tab_width spaces from start of line
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                tab_width,
            )
            selected = cursor.selectedText()
            # Remove leading spaces only
            spaces = len(selected) - len(selected.lstrip(" "))
            if spaces > 0:
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    min(spaces, tab_width),
                )
                cursor.removeSelectedText()
            return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Auto-indent: match the indentation of the current line
            cursor = self.textCursor()
            block_text = cursor.block().text()
            indent = ""
            for ch in block_text:
                if ch in (" ", "\t"):
                    indent += ch
                else:
                    break
            # If line ends with a block-opening keyword, add extra indent
            stripped = block_text.strip()
            if stripped and any(
                stripped.startswith(kw)
                for kw in ("if ", "while ", "sub ", "else")
            ):
                indent += " " * tab_width

            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        super().keyPressEvent(event)

    # =========================================================================
    # Dirty State
    # =========================================================================

    def _on_contents_change(self, position: int, chars_removed: int, chars_added: int):
        """Track when the document has been modified.

        Bound to QTextDocument.contentsChange rather than QPlainTextEdit's
        plain textChanged: a syntax-highlighter rehighlight() (e.g. on a
        theme switch) fires textChanged with no characters actually
        inserted or removed, which was marking a pristine new file dirty
        before the user had typed anything.
        """
        if chars_removed == 0 and chars_added == 0:
            return
        if not self._modified:
            self._modified = True
            self.file_modified.emit(True)

    @property
    def is_modified(self) -> bool:
        return self._modified

    def set_clean(self):
        """Mark the document as clean (just saved)."""
        self._modified = False
        self.file_modified.emit(False)
