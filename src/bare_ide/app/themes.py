"""Theme Manager for BARE IDE.

Provides 6 built-in UI themes matching the Fragillidae IDE Suite standard:
  Dark, Light, Grey, Solarized Light, Solarized Dark, High Contrast

BARE accent colors: Blue (primary/keywords) and Amber (secondary/builtins).

Each theme defines:
  - Full UI color palette (backgrounds, panels, buttons, etc.)
  - Syntax highlighting colors for BARE token categories
  - Scope depth colors for nested block coloring (Phase 6)
"""

from dataclasses import dataclass, field
from typing import Dict, List

from bare_ide.app.settings import SettingsManager


@dataclass
class SyntaxColors:
    """Syntax highlighting colors for the code editor."""

    keyword: str = "#569cd6"        # Blue — print, if, while, sub, etc.
    builtin: str = "#e5a645"        # Amber — len, append, str, num, random
    string: str = "#98c379"         # Green
    number: str = "#d19a66"         # Orange
    comment: str = "#5c6370"        # Gray, italic
    literal: str = "#56b6c2"        # Teal — true, false, null
    operator: str = "#c678dd"       # Purple
    identifier: str = "#abb2bf"     # Default text


@dataclass
class UITheme:
    """Complete UI theme definition."""

    name: str
    is_dark: bool

    # Main colors
    background: str
    foreground: str
    accent: str
    accent_hover: str

    # Panel colors
    panel_background: str
    panel_border: str

    # File browser colors
    browser_background: str
    browser_item_hover: str
    browser_item_selected: str

    # Editor colors
    editor_background: str
    editor_foreground: str
    editor_line_highlight: str
    editor_selection: str
    editor_gutter_bg: str
    editor_gutter_fg: str

    # Terminal colors
    terminal_background: str
    terminal_foreground: str

    # Scrollbar
    scrollbar_background: str
    scrollbar_handle: str
    scrollbar_handle_hover: str

    # Button colors
    button_background: str
    button_foreground: str
    button_hover: str
    button_pressed: str

    # Input colors
    input_background: str
    input_border: str
    input_focus_border: str

    # Status colors
    success: str
    warning: str
    error: str
    info: str

    # Syntax colors for this theme
    syntax: SyntaxColors = field(default_factory=SyntaxColors)

    # Scope depth colors for nested block coloring
    scope_depth_colors: List[str] = field(
        default_factory=lambda: ["#f9c74f", "#577590", "#90be6d", "#9b5de5"]
    )


# =============================================================================
# Built-in Themes — 6 themes matching the IDE Suite standard
# =============================================================================

DARK_THEME = UITheme(
    name="Dark",
    is_dark=True,
    background="#1e1e2e",
    foreground="#cdd6f4",
    accent="#89b4fa",          # Blue accent
    accent_hover="#74c7ec",
    panel_background="#181825",
    panel_border="#313244",
    browser_background="#181825",
    browser_item_hover="#585b70",
    browser_item_selected="#89b4fa",
    editor_background="#1e1e2e",
    editor_foreground="#cdd6f4",
    editor_line_highlight="#2a2a3c",
    editor_selection="#44475a",
    editor_gutter_bg="#181825",
    editor_gutter_fg="#6c7086",
    terminal_background="#11111b",
    terminal_foreground="#cdd6f4",
    scrollbar_background="#181825",
    scrollbar_handle="#45475a",
    scrollbar_handle_hover="#585b70",
    button_background="#45475a",
    button_foreground="#cdd6f4",
    button_hover="#585b70",
    button_pressed="#313244",
    input_background="#313244",
    input_border="#45475a",
    input_focus_border="#89b4fa",
    success="#a6e3a1",
    warning="#f9e2af",
    error="#f38ba8",
    info="#89b4fa",
    syntax=SyntaxColors(
        keyword="#89b4fa",       # Blue
        builtin="#f9e2af",       # Amber
        string="#a6e3a1",        # Green
        number="#fab387",        # Peach
        comment="#6c7086",       # Overlay
        literal="#94e2d5",       # Teal
        operator="#cba6f7",      # Mauve
        identifier="#cdd6f4",    # Text
    ),
    scope_depth_colors=["#f9e2af", "#89b4fa", "#a6e3a1", "#cba6f7"],
)


LIGHT_THEME = UITheme(
    name="Light",
    is_dark=False,
    background="#eff1f5",
    foreground="#4c4f69",
    accent="#1e66f5",
    accent_hover="#2a7afd",
    panel_background="#e6e9ef",
    panel_border="#bcc0cc",
    browser_background="#e6e9ef",
    browser_item_hover="#acb0be",
    browser_item_selected="#1e66f5",
    editor_background="#eff1f5",
    editor_foreground="#4c4f69",
    editor_line_highlight="#dce0e8",
    editor_selection="#acb0be",
    editor_gutter_bg="#e6e9ef",
    editor_gutter_fg="#8c8fa1",
    terminal_background="#dce0e8",
    terminal_foreground="#4c4f69",
    scrollbar_background="#e6e9ef",
    scrollbar_handle="#bcc0cc",
    scrollbar_handle_hover="#acb0be",
    button_background="#bcc0cc",
    button_foreground="#4c4f69",
    button_hover="#acb0be",
    button_pressed="#ccd0da",
    input_background="#ccd0da",
    input_border="#bcc0cc",
    input_focus_border="#1e66f5",
    success="#40a02b",
    warning="#df8e1d",
    error="#d20f39",
    info="#1e66f5",
    syntax=SyntaxColors(
        keyword="#1e66f5",       # Blue
        builtin="#df8e1d",       # Amber/yellow
        string="#40a02b",        # Green
        number="#fe640b",        # Orange
        comment="#8c8fa1",       # Gray
        literal="#179299",       # Teal
        operator="#8839ef",      # Purple
        identifier="#4c4f69",    # Dark text
    ),
    scope_depth_colors=["#df8e1d", "#1e66f5", "#40a02b", "#8839ef"],
)


GREY_THEME = UITheme(
    name="Grey",
    is_dark=True,
    background="#2b2d30",
    foreground="#bcbec4",
    accent="#4a9eff",
    accent_hover="#5eadff",
    panel_background="#25262a",
    panel_border="#3c3f41",
    browser_background="#25262a",
    browser_item_hover="#5a5d62",
    browser_item_selected="#4a9eff",
    editor_background="#2b2d30",
    editor_foreground="#bcbec4",
    editor_line_highlight="#323437",
    editor_selection="#214283",
    editor_gutter_bg="#25262a",
    editor_gutter_fg="#6c6f73",
    terminal_background="#1e1f22",
    terminal_foreground="#bcbec4",
    scrollbar_background="#25262a",
    scrollbar_handle="#4a5157",
    scrollbar_handle_hover="#5a5d62",
    button_background="#4a5157",
    button_foreground="#bcbec4",
    button_hover="#5a5d62",
    button_pressed="#3c3f41",
    input_background="#3c3f41",
    input_border="#4a5157",
    input_focus_border="#4a9eff",
    success="#6aab73",
    warning="#d5b778",
    error="#c75450",
    info="#4a9eff",
    syntax=SyntaxColors(
        keyword="#6897bb",
        builtin="#d5b778",
        string="#6a8759",
        number="#d19a66",
        comment="#6c6f73",
        literal="#6897bb",
        operator="#cc7832",
        identifier="#bcbec4",
    ),
    scope_depth_colors=["#d5b778", "#4a9eff", "#6aab73", "#b58ee0"],
)


SOLARIZED_LIGHT_THEME = UITheme(
    name="Solarized Light",
    is_dark=False,
    background="#fdf6e3",
    foreground="#657b83",
    accent="#268bd2",
    accent_hover="#2aa1f5",
    panel_background="#eee8d5",
    panel_border="#93a1a1",
    browser_background="#eee8d5",
    browser_item_hover="#839496",
    browser_item_selected="#268bd2",
    editor_background="#fdf6e3",
    editor_foreground="#657b83",
    editor_line_highlight="#eee8d5",
    editor_selection="#eee8d5",
    editor_gutter_bg="#eee8d5",
    editor_gutter_fg="#93a1a1",
    terminal_background="#eee8d5",
    terminal_foreground="#657b83",
    scrollbar_background="#eee8d5",
    scrollbar_handle="#93a1a1",
    scrollbar_handle_hover="#839496",
    button_background="#93a1a1",
    button_foreground="#fdf6e3",
    button_hover="#839496",
    button_pressed="#eee8d5",
    input_background="#eee8d5",
    input_border="#93a1a1",
    input_focus_border="#268bd2",
    success="#859900",
    warning="#b58900",
    error="#dc322f",
    info="#268bd2",
    syntax=SyntaxColors(
        keyword="#268bd2",
        builtin="#b58900",
        string="#859900",
        number="#cb4b16",
        comment="#93a1a1",
        literal="#2aa198",
        operator="#d33682",
        identifier="#657b83",
    ),
    scope_depth_colors=["#b58900", "#268bd2", "#859900", "#6c71c4"],
)


SOLARIZED_DARK_THEME = UITheme(
    name="Solarized Dark",
    is_dark=True,
    background="#002b36",
    foreground="#839496",
    accent="#268bd2",
    accent_hover="#2aa1f5",
    panel_background="#073642",
    panel_border="#586e75",
    browser_background="#073642",
    browser_item_hover="#657b83",
    browser_item_selected="#268bd2",
    editor_background="#002b36",
    editor_foreground="#839496",
    editor_line_highlight="#073642",
    editor_selection="#073642",
    editor_gutter_bg="#073642",
    editor_gutter_fg="#586e75",
    terminal_background="#073642",
    terminal_foreground="#839496",
    scrollbar_background="#073642",
    scrollbar_handle="#586e75",
    scrollbar_handle_hover="#657b83",
    button_background="#586e75",
    button_foreground="#fdf6e3",
    button_hover="#657b83",
    button_pressed="#073642",
    input_background="#073642",
    input_border="#586e75",
    input_focus_border="#268bd2",
    success="#859900",
    warning="#b58900",
    error="#dc322f",
    info="#268bd2",
    syntax=SyntaxColors(
        keyword="#268bd2",
        builtin="#b58900",
        string="#859900",
        number="#cb4b16",
        comment="#586e75",
        literal="#2aa198",
        operator="#d33682",
        identifier="#839496",
    ),
    scope_depth_colors=["#b58900", "#268bd2", "#859900", "#6c71c4"],
)


HIGH_CONTRAST_THEME = UITheme(
    name="High Contrast",
    is_dark=True,
    background="#000000",
    foreground="#ffffff",
    accent="#4fc3f7",
    accent_hover="#81d4fa",
    panel_background="#0a0a0a",
    panel_border="#444444",
    browser_background="#0a0a0a",
    browser_item_hover="#555555",
    browser_item_selected="#4fc3f7",
    editor_background="#000000",
    editor_foreground="#ffffff",
    editor_line_highlight="#1a1a1a",
    editor_selection="#264f78",
    editor_gutter_bg="#0a0a0a",
    editor_gutter_fg="#888888",
    terminal_background="#0a0a0a",
    terminal_foreground="#ffffff",
    scrollbar_background="#0a0a0a",
    scrollbar_handle="#555555",
    scrollbar_handle_hover="#777777",
    button_background="#333333",
    button_foreground="#ffffff",
    button_hover="#555555",
    button_pressed="#222222",
    input_background="#1a1a1a",
    input_border="#555555",
    input_focus_border="#4fc3f7",
    success="#00ff00",
    warning="#ffff00",
    error="#ff4444",
    info="#4fc3f7",
    syntax=SyntaxColors(
        keyword="#6dcfff",
        builtin="#ffd700",
        string="#00ff7f",
        number="#ff8c00",
        comment="#888888",
        literal="#00e5ff",
        operator="#ff69b4",
        identifier="#ffffff",
    ),
    scope_depth_colors=["#ffd700", "#6dcfff", "#00ff7f", "#ff69b4"],
)


# Registry mapping theme name to UITheme
THEMES: Dict[str, UITheme] = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "grey": GREY_THEME,
    "solarized_light": SOLARIZED_LIGHT_THEME,
    "solarized_dark": SOLARIZED_DARK_THEME,
    "high_contrast": HIGH_CONTRAST_THEME,
}


class ThemeManager:
    """Manages theme loading and stylesheet generation."""

    def __init__(self, settings: SettingsManager):
        self.settings = settings
        self._current_theme = self._resolve_theme()

    def _resolve_theme(self) -> UITheme:
        """Look up the current theme from settings."""
        name = self.settings.settings.theme.ui_theme
        return THEMES.get(name, DARK_THEME)

    @property
    def current_theme(self) -> UITheme:
        return self._current_theme

    def set_theme(self, name: str) -> None:
        """Switch to a different theme."""
        if name in THEMES:
            self.settings.settings.theme.ui_theme = name
            self._current_theme = THEMES[name]
            self.settings.save()

    def get_theme_names(self) -> List[str]:
        """Return list of available theme display names."""
        return [t.name for t in THEMES.values()]

    def get_current_stylesheet(self) -> str:
        """Generate the full QSS stylesheet for the current theme."""
        t = self._current_theme
        return f"""
            /* ========== Global ========== */
            QMainWindow {{
                background-color: {t.background};
                color: {t.foreground};
            }}
            QWidget {{
                background-color: {t.background};
                color: {t.foreground};
            }}

            /* ========== Menu Bar ========== */
            QMenuBar {{
                background-color: {t.panel_background};
                color: {t.foreground};
                border-bottom: 1px solid {t.panel_border};
                padding: 2px 0px;
            }}
            QMenuBar::item {{
                padding: 4px 10px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {t.button_hover};
            }}
            QMenu {{
                background-color: {t.panel_background};
                color: {t.foreground};
                border: 1px solid {t.panel_border};
                padding: 4px 0px;
            }}
            QMenu::item {{
                padding: 6px 30px 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: {t.accent};
                color: {t.button_foreground};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {t.panel_border};
                margin: 4px 10px;
            }}

            /* ========== Toolbar ========== */
            QToolBar {{
                background-color: {t.panel_background};
                border-bottom: 1px solid {t.panel_border};
                padding: 4px;
                spacing: 4px;
            }}
            QToolButton {{
                background-color: {t.button_background};
                color: {t.button_foreground};
                border: 1px solid {t.panel_border};
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 12px;
            }}
            QToolButton:hover {{
                background-color: {t.button_hover};
                border-color: {t.accent};
            }}
            QToolButton:pressed {{
                background-color: {t.button_pressed};
            }}
            QToolButton:disabled {{
                opacity: 0.5;
                color: {t.editor_gutter_fg};
            }}

            /* ========== Status Bar ========== */
            QStatusBar {{
                background-color: {t.panel_background};
                color: {t.foreground};
                border-top: 1px solid {t.panel_border};
                font-size: 11px;
            }}
            QStatusBar::item {{
                border: none;
            }}
            QStatusBar QLabel {{
                padding: 2px 8px;
            }}

            /* ========== Splitter ========== */
            QSplitter::handle {{
                background-color: {t.panel_border};
            }}
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            QSplitter::handle:vertical {{
                height: 2px;
            }}

            /* ========== Scrollbars ========== */
            QScrollBar:vertical {{
                background-color: {t.scrollbar_background};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {t.scrollbar_handle};
                min-height: 30px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {t.scrollbar_handle_hover};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {t.scrollbar_background};
                height: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {t.scrollbar_handle};
                min-width: 30px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {t.scrollbar_handle_hover};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            /* ========== Labels for panels ========== */
            QLabel#panel_label {{
                color: {t.editor_gutter_fg};
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                text-transform: uppercase;
            }}
        """
