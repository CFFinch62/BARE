"""Settings Manager for BARE IDE.

Handles loading, saving, and managing user preferences.
Follows the same JSON-file-based pattern as the sibling IDE Suite projects.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List


def get_config_dir() -> Path:
    """Get the configuration directory for BARE IDE."""
    config_dir = Path.home() / ".config" / "bare_ide"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@dataclass
class EditorSettings:
    """Editor-specific settings."""

    font_family: str = "JetBrains Mono"
    font_size: int = 13
    tab_width: int = 4
    show_line_numbers: bool = True
    word_wrap: bool = False
    highlight_current_line: bool = True
    scope_boxes_enabled: bool = True


@dataclass
class ThemeSettings:
    """Theme-related settings."""

    ui_theme: str = "dark"


@dataclass
class WindowSettings:
    """Window state settings."""

    width: int = 1100
    height: int = 750
    maximized: bool = False
    splitter_sizes: List[int] = field(default_factory=lambda: [600, 300])


@dataclass
class Settings:
    """All IDE settings."""

    editor: EditorSettings = field(default_factory=EditorSettings)
    theme: ThemeSettings = field(default_factory=ThemeSettings)
    window: WindowSettings = field(default_factory=WindowSettings)
    recent_files: List[str] = field(default_factory=list)


class SettingsManager:
    """Manages loading and saving of settings."""

    def __init__(self):
        self.config_file = get_config_dir() / "settings.json"
        self.settings = self._load()

    def _load(self) -> Settings:
        """Load settings from file or create defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return self._dict_to_settings(data)
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")
        return Settings()

    def _dict_to_settings(self, data: dict) -> Settings:
        """Convert dictionary to Settings object, handling missing fields gracefully."""
        settings = Settings()
        if "editor" in data:
            for k, v in data["editor"].items():
                if hasattr(settings.editor, k):
                    setattr(settings.editor, k, v)
        if "theme" in data:
            for k, v in data["theme"].items():
                if hasattr(settings.theme, k):
                    setattr(settings.theme, k, v)
        if "window" in data:
            for k, v in data["window"].items():
                if hasattr(settings.window, k):
                    setattr(settings.window, k, v)
        if "recent_files" in data:
            settings.recent_files = data["recent_files"]
        return settings

    def save(self):
        """Save settings to file."""
        data = {
            "editor": asdict(self.settings.editor),
            "theme": asdict(self.settings.theme),
            "window": asdict(self.settings.window),
            "recent_files": self.settings.recent_files[:20],
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")

    def add_recent_file(self, filepath: str):
        """Add a file to the recent files list."""
        if filepath in self.settings.recent_files:
            self.settings.recent_files.remove(filepath)
        self.settings.recent_files.insert(0, filepath)
        self.settings.recent_files = self.settings.recent_files[:20]
        self.save()
