"""
Theme system for phoenix-docgen.

Loads theme configuration from a theme.yaml file and provides access to
colours, fonts, organisation details, cover template paths, and document
defaults.  A global config file (~/.config/phoenix-docgen/config.yaml)
controls the themes directory and default theme selection.
"""

import os
import platform
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent

# ── Global config file locations ─────────────────────────────────────

def _default_config_path():
    """Return the platform-appropriate default config path."""
    if platform.system() == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "phoenix-docgen" / "config.yaml"
    return Path.home() / ".config" / "phoenix-docgen" / "config.yaml"


def load_config(config_path=None):
    """Load the global phoenix-docgen configuration.

    Priority: config_path arg → PHOENIX_CONFIG env → default platform path.
    Returns an empty dict if the file doesn't exist (all values optional).
    """
    if config_path is None:
        config_path = os.environ.get("PHOENIX_CONFIG")
    if config_path is None:
        config_path = _default_config_path()

    config_path = Path(config_path).expanduser()
    if not config_path.exists():
        return {}

    try:
        return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError) as exc:
        print(f"  WARNING: Could not load config {config_path}: {exc}")
        return {}


# ── Built-in fallback defaults (used when no theme is loaded) ────────

BUILTIN_DEFAULTS = {
    "organisation": {
        "name": "",
        "short_name": "",
        "address": "",
    },
    "defaults": {
        "subtitle": "",
        "author": "",
        "classification": "[RESTRICTED]",
    },
    "colours": {
        "primary": "#2c3e50",
        "secondary": "#34495e",
        "accent": "#2980b9",
    },
    "fonts": {
        "family": "sans-serif",
        "fallback": "Arial, Helvetica, sans-serif",
    },
    "cover": {
        "logo_position": {"x": 85, "y": 75, "width": 108, "height": 108},
    },
}


# ── Theme class ──────────────────────────────────────────────────────

class Theme:
    """A loaded theme with access to colours, fonts, org details, and assets."""

    def __init__(self, theme_dir):
        self.theme_dir = Path(theme_dir)
        yaml_path = self.theme_dir / "theme.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"Theme config not found: {yaml_path}")

        self._data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        self.name = self._data.get("name", self.theme_dir.name)
        self.display_name = self._data.get("display_name", self.name)

    # ── Organisation ─────────────────────────────────────────────────

    def org(self, key):
        """Get an organisation field (name, short_name, address)."""
        return self._data.get("organisation", {}).get(
            key, BUILTIN_DEFAULTS["organisation"].get(key, "")
        )

    # ── Colours ──────────────────────────────────────────────────────

    def colour(self, key):
        """Get a colour value by key (primary, secondary, accent)."""
        return self._data.get("colours", {}).get(
            key, BUILTIN_DEFAULTS["colours"].get(key, "#000000")
        )

    # ── Fonts ────────────────────────────────────────────────────────

    def font_family(self):
        """Return the font family name."""
        return self._data.get("fonts", {}).get(
            "family", BUILTIN_DEFAULTS["fonts"]["family"]
        )

    def font_fallback(self):
        """Return the CSS fallback font stack."""
        return self._data.get("fonts", {}).get(
            "fallback", BUILTIN_DEFAULTS["fonts"]["fallback"]
        )

    def font_stack(self):
        """Return the complete CSS font-family value."""
        return f"'{self.font_family()}', {self.font_fallback()}"

    def font_weights(self):
        """Return dict of weight → absolute Path to TTF file.

        Font filenames in theme.yaml are relative to the theme directory.
        """
        weights_cfg = self._data.get("fonts", {}).get("weights", {})
        result = {}
        fonts_dir = self.theme_dir / "fonts"
        for weight, filename in weights_cfg.items():
            path = fonts_dir / filename
            if path.exists():
                result[int(weight)] = path
        return result

    # ── Cover assets ─────────────────────────────────────────────────

    def cover_template_path(self):
        """Return the absolute path to the SVG cover template."""
        filename = self._data.get("cover", {}).get(
            "template", "cover-page-template-a4.svg"
        )
        return self.theme_dir / filename

    def logo_path(self):
        """Return the absolute path to the logo file."""
        filename = self._data.get("cover", {}).get("logo", "logo.png")
        return self.theme_dir / filename

    def logo_position(self):
        """Return logo position dict with x, y, width, height."""
        return self._data.get("cover", {}).get(
            "logo_position",
            BUILTIN_DEFAULTS["cover"]["logo_position"],
        )

    # ── Document defaults ────────────────────────────────────────────

    def doc_defaults(self):
        """Return default document metadata from the theme.

        Keys: subtitle, author, classification.
        """
        return dict(
            BUILTIN_DEFAULTS["defaults"],
            **self._data.get("defaults", {}),
        )


# ── Theme resolution ─────────────────────────────────────────────────

def resolve_themes_dir(cli_path=None, config=None):
    """Determine the themes directory.

    Priority: cli_path → PHOENIX_THEMES_DIR env → config themes_dir → default.
    """
    if cli_path:
        return Path(cli_path).expanduser().resolve()

    env_path = os.environ.get("PHOENIX_THEMES_DIR")
    if env_path:
        return Path(env_path).expanduser().resolve()

    if config and config.get("themes_dir"):
        return Path(config["themes_dir"]).expanduser().resolve()

    # Default: check beside scripts, then parent (handles repo layout
    # where scripts are in src/ and themes are at repo root).
    for candidate in (SCRIPT_DIR / "themes", SCRIPT_DIR.parent / "themes"):
        if candidate.is_dir():
            return candidate.resolve()

    return SCRIPT_DIR / "themes"


def resolve_theme(name=None, themes_dir=None, config=None):
    """Resolve and load a Theme, or return None.

    Priority for theme name: name arg → PHOENIX_THEME env →
    config default_theme → auto-detect (single theme) → None.
    """
    if themes_dir is None:
        themes_dir = resolve_themes_dir(config=config)
    else:
        themes_dir = Path(themes_dir)

    if not themes_dir.is_dir():
        return None

    # Determine which theme name to use
    if not name:
        name = os.environ.get("PHOENIX_THEME")
    if not name and config:
        name = config.get("default_theme")
    if not name:
        # Auto-detect: if exactly one theme directory exists, use it
        subdirs = [d for d in themes_dir.iterdir() if d.is_dir() and (d / "theme.yaml").exists()]
        if len(subdirs) == 1:
            name = subdirs[0].name
        else:
            return None

    theme_path = themes_dir / name
    if not (theme_path / "theme.yaml").exists():
        print(f"  WARNING: Theme '{name}' not found at {theme_path}")
        return None

    return Theme(theme_path)
