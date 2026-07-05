"""BARE IDE — Entry Point.

Creates the QApplication, loads settings and theme, and shows the main
window. BARE is IDE-locked: this is the only supported way to run .bare
programs.
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from bare_ide.app.settings import SettingsManager
from bare_ide.app.themes import ThemeManager
from bare_ide.app.main_window import BareIDEMainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("BARE IDE")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Fragillidae Software")

    if hasattr(sys, "_MEIPASS"):
        root_dir = Path(sys._MEIPASS)
    else:
        # main.py -> bare_ide -> src -> BARE
        root_dir = Path(__file__).resolve().parent.parent.parent

    icon_path = root_dir / "icons" / "bare_icon.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    settings = SettingsManager()
    theme_manager = ThemeManager(settings)
    app.setStyleSheet(theme_manager.get_current_stylesheet())

    window = BareIDEMainWindow(settings, theme_manager, docs_dir=root_dir / "docs")
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
