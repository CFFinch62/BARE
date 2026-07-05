"""Syntax Highlighter for BARE IDE.

Regex-based QSyntaxHighlighter covering the token categories from
BARE_ide_plan.md: keywords, builtins, strings, numbers, comments, and
boolean/null literals. Colors come from the active theme's SyntaxColors
(bare_ide.app.themes), so switching themes just calls set_theme().

`input` is classified as a keyword only, matching the implementation
plan's resolution of the spec's keyword/builtin overlap (highlight as
keyword, implement as builtin).
"""

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat

from bare_ide.app.themes import UITheme

KEYWORDS = r"\b(print|input|if|else|end|while|sub|return|and|or|not)\b"
BUILTINS = r"\b(len|append|str|num|random|round)\b"
LITERALS = r"\b(true|false|null)\b"
NUMBER = r"\b\d+(\.\d+)?\b"
STRING = r'"[^"]*"'
COMMENT = r"#.*$"


class BareHighlighter(QSyntaxHighlighter):
    """Highlights BARE source code by token category."""

    def __init__(self, document, theme: UITheme = None):
        super().__init__(document)
        self._rules = []
        self.set_theme(theme)

    def set_theme(self, theme: UITheme):
        """Rebuild highlighting rules for a new theme and rehighlight."""
        self.theme = theme
        syntax = theme.syntax if theme else None

        def fmt(color: str, italic: bool = False, bold: bool = False) -> QTextCharFormat:
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if italic:
                f.setFontItalic(True)
            if bold:
                f.setFontWeight(QFont.Weight.Bold)
            return f

        keyword_color = syntax.keyword if syntax else "#569cd6"
        builtin_color = syntax.builtin if syntax else "#e5a645"
        string_color = syntax.string if syntax else "#98c379"
        number_color = syntax.number if syntax else "#d19a66"
        comment_color = syntax.comment if syntax else "#5c6370"
        literal_color = syntax.literal if syntax else "#56b6c2"

        # Rules are applied in order and later rules overwrite earlier ones
        # on overlapping spans — strings must beat keywords/numbers inside
        # them, and comments must beat everything from '#' to end of line.
        self._rules = [
            (QRegularExpression(KEYWORDS), fmt(keyword_color, bold=True)),
            (QRegularExpression(BUILTINS), fmt(builtin_color)),
            (QRegularExpression(LITERALS), fmt(literal_color)),
            (QRegularExpression(NUMBER), fmt(number_color)),
            (QRegularExpression(STRING), fmt(string_color)),
            (QRegularExpression(COMMENT), fmt(comment_color, italic=True)),
        ]
        self.rehighlight()

    def highlightBlock(self, text: str):
        for pattern, text_format in self._rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)
