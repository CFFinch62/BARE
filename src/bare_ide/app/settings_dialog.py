"""Preferences Dialog for BARE IDE.

A single-page settings form — BARE's settings surface is small enough
(theme, font, tab width, wrap, scope boxes) that the tabbed dialogs used
by the larger sibling IDEs would be overkill here.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFontComboBox,
    QFormLayout,
    QSpinBox,
    QVBoxLayout,
)

from bare_ide.app.settings import SettingsManager
from bare_ide.app.themes import THEMES, ThemeManager


class SettingsDialog(QDialog):
    """Preferences dialog. Emits settings_applied so the caller can refresh
    the editor/console/theme without this dialog needing to know about them."""

    settings_applied = pyqtSignal()

    def __init__(self, settings: SettingsManager, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_manager = theme_manager
        self._theme_keys = list(THEMES.keys())

        self.setWindowTitle("Preferences")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        s = self.settings.settings

        self.theme_combo = QComboBox()
        self.theme_combo.addItems([THEMES[k].name for k in self._theme_keys])
        if s.theme.ui_theme in self._theme_keys:
            self.theme_combo.setCurrentIndex(self._theme_keys.index(s.theme.ui_theme))
        form.addRow("Theme:", self.theme_combo)

        self.font_combo = QFontComboBox()
        idx = self.font_combo.findText(s.editor.font_family)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        else:
            self.font_combo.setEditText(s.editor.font_family)
        form.addRow("Editor font:", self.font_combo)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 32)
        self.font_size.setValue(s.editor.font_size)
        form.addRow("Font size:", self.font_size)

        self.tab_width = QSpinBox()
        self.tab_width.setRange(2, 8)
        self.tab_width.setValue(s.editor.tab_width)
        form.addRow("Tab width:", self.tab_width)

        self.word_wrap = QCheckBox("Wrap long lines")
        self.word_wrap.setChecked(s.editor.word_wrap)
        form.addRow("", self.word_wrap)

        self.scope_boxes = QCheckBox("Shade nested if/while/sub blocks")
        self.scope_boxes.setChecked(s.editor.scope_boxes_enabled)
        form.addRow("Scope boxes:", self.scope_boxes)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply)
        layout.addWidget(buttons)

    def _apply(self):
        s = self.settings.settings
        s.theme.ui_theme = self._theme_keys[self.theme_combo.currentIndex()]
        s.editor.font_family = self.font_combo.currentFont().family()
        s.editor.font_size = self.font_size.value()
        s.editor.tab_width = self.tab_width.value()
        s.editor.word_wrap = self.word_wrap.isChecked()
        s.editor.scope_boxes_enabled = self.scope_boxes.isChecked()

        self.theme_manager.set_theme(s.theme.ui_theme)
        self.settings.save()
        self.settings_applied.emit()

    def _save_and_close(self):
        self._apply()
        self.accept()
