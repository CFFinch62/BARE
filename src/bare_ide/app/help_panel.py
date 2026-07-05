"""User Guide Panel for BARE IDE.

A dockable Markdown viewer for docs/user-guide.md, so the documentation
can sit alongside the editor (right dock, tabbed with Variable Watch)
instead of forcing the user to alt-tab to a browser. Internal links
between user-guide.md and language-spec.md are resolved in place rather
than handed to the desktop's default handler; anything else (an external
http(s) link) opens in the system browser instead.
"""

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDockWidget, QLabel, QTextBrowser, QVBoxLayout, QWidget

from bare_ide.app.themes import UITheme

HOME_DOC = "user-guide.md"


class HelpPane(QDockWidget):
    """Dockable Markdown viewer showing a BARE doc (user guide or language spec)."""

    def __init__(
        self,
        docs_dir: Path,
        parent=None,
        title: str = "User Guide",
        home_doc: str = HOME_DOC,
        object_name: str = "user_guide_dock",
    ):
        super().__init__(title, parent)
        self.setObjectName(object_name)
        self._docs_dir = docs_dir

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QLabel(f"  {title.upper()}")
        self.header.setObjectName("panel_label")
        self.header.setFixedHeight(24)
        layout.addWidget(self.header)

        self.browser = QTextBrowser(container)
        self.browser.setOpenLinks(False)
        self.browser.setOpenExternalLinks(False)
        self.browser.anchorClicked.connect(self._on_anchor_clicked)
        layout.addWidget(self.browser)

        self.setWidget(container)
        self._load_doc(home_doc)

    def _load_doc(self, filename: str) -> None:
        path = self._docs_dir / filename
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            self.browser.setPlainText(f"Could not load {filename}.")
            return
        self.browser.setSearchPaths([str(self._docs_dir)])
        self.browser.setMarkdown(text)

    def _on_anchor_clicked(self, url: QUrl) -> None:
        if not url.scheme() or url.scheme() == "file":
            target = Path(url.path()).name
            if target.endswith(".md"):
                self._load_doc(target)
                return
        QDesktopServices.openUrl(url)

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
        self.browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {theme.panel_background};
                color: {theme.foreground};
                border: none;
            }}
        """)
