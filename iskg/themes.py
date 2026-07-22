"""Named theme definitions for ISKG.

Each theme is a dict of CSS custom property overrides applied on top of
the default IFAZ style sheet (``iskg.theme.IFAZ_CSS``).

Usage::

    from iskg.themes import THEMES, apply_theme_js

    # Get JS to switch to a named theme
    js = apply_theme_js("cold")
    app.execute_js(js)

    # Or via Application convenience method
    app.set_theme("warm")
"""

from __future__ import annotations

THEMES: dict[str, dict[str, str]] = {
    "ifaz": {
        "--bg-primary": "#070b10",
        "--bg-panel": "#0c111a",
        "--bg-panel-alt": "#111822",
        "--bg-panel-hi": "#16202e",
        "--border": "#1a2636",
        "--border-light": "#28364a",
        "--green": "#4ade80",
        "--green-dim": "#0f2e1a",
        "--amber": "#f59e0b",
        "--amber-dim": "#2e2008",
        "--red": "#ef4444",
        "--red-dim": "#2e0e0e",
        "--cyan": "#22d3ee",
        "--cyan-dim": "#0a2030",
        "--text": "#c8d6e5",
        "--text-dim": "#4a5a6a",
        "--text-green": "#7ec850",
        "--progress-from": "#0f2e1a",
        "--progress-to": "#2e2008",
    },
    "desert": {
        "--bg-primary": "#1a1410",
        "--bg-panel": "#221c16",
        "--bg-panel-alt": "#2a241e",
        "--bg-panel-hi": "#342e26",
        "--border": "#3a342c",
        "--border-light": "#4a443a",
        "--green": "#a3b18a",
        "--green-dim": "#1a2214",
        "--amber": "#d4a373",
        "--amber-dim": "#2a2016",
        "--red": "#e07a5f",
        "--red-dim": "#2e1810",
        "--cyan": "#8ecae6",
        "--cyan-dim": "#10202a",
        "--text": "#d4c9b8",
        "--text-dim": "#6a5f52",
        "--text-green": "#a3b18a",
        "--progress-from": "#1a2214",
        "--progress-to": "#2a2016",
    },
    "infinity": {
        "--bg-primary": "#050510",
        "--bg-panel": "#0a0a1a",
        "--bg-panel-alt": "#101025",
        "--bg-panel-hi": "#181838",
        "--border": "#1a1a3a",
        "--border-light": "#282858",
        "--green": "#00ffc8",
        "--green-dim": "#002a20",
        "--amber": "#ff6600",
        "--amber-dim": "#2a1000",
        "--red": "#ff3355",
        "--red-dim": "#2e0008",
        "--cyan": "#00d4ff",
        "--cyan-dim": "#002a38",
        "--text": "#e0e0ff",
        "--text-dim": "#6060a0",
        "--text-green": "#00ffc8",
        "--progress-from": "#002a20",
        "--progress-to": "#002a38",
    },
    "cyberdusk": {
        "--bg-primary": "#080c1a",
        "--bg-panel": "#0e1428",
        "--bg-panel-alt": "#141c34",
        "--bg-panel-hi": "#1c2640",
        "--border": "#222e4a",
        "--border-light": "#2e3c5c",
        "--green": "#4ade80",
        "--green-dim": "#0a1e12",
        "--amber": "#fbbf24",
        "--amber-dim": "#1e1a06",
        "--red": "#ef4444",
        "--red-dim": "#2a0a0a",
        "--cyan": "#38bdf8",
        "--cyan-dim": "#0a2035",
        "--text": "#c8d6e5",
        "--text-dim": "#4a5a7a",
        "--text-green": "#60a5fa",
        "--progress-from": "#0a2035",
        "--progress-to": "#1a1a3a",
    },
    "light": {
        "--bg-primary": "#e8eaed",
        "--bg-panel": "#f2f3f5",
        "--bg-panel-alt": "#e2e4e8",
        "--bg-panel-hi": "#d5d7db",
        "--border": "#b0b3b8",
        "--border-light": "#c4c7cc",
        "--green": "#2e7d32",
        "--green-dim": "#e8f5e9",
        "--amber": "#e65100",
        "--amber-dim": "#fff3e0",
        "--red": "#c62828",
        "--red-dim": "#ffebee",
        "--cyan": "#00838f",
        "--cyan-dim": "#e0f7fa",
        "--text": "#202124",
        "--text-dim": "#5f6368",
        "--text-green": "#2e7d32",
        "--progress-from": "#e8f5e9",
        "--progress-to": "#fff3e0",
    },
    "dracula": {
        "--bg-primary": "#282a36",
        "--bg-panel": "#2d2f3e",
        "--bg-panel-alt": "#363848",
        "--bg-panel-hi": "#404254",
        "--border": "#44475a",
        "--border-light": "#525466",
        "--green": "#50fa7b",
        "--green-dim": "#1a2e1a",
        "--amber": "#f1fa8c",
        "--amber-dim": "#2a2a10",
        "--red": "#ff5555",
        "--red-dim": "#2e0e0e",
        "--cyan": "#8be9fd",
        "--cyan-dim": "#0a2a32",
        "--text": "#f8f8f2",
        "--text-dim": "#6a6a8a",
        "--text-green": "#50fa7b",
        "--progress-from": "#1a2e1a",
        "--progress-to": "#2a2a10",
    },
    "nord": {
        "--bg-primary": "#2e3440",
        "--bg-panel": "#353b4a",
        "--bg-panel-alt": "#3b4252",
        "--bg-panel-hi": "#434c5e",
        "--border": "#4c566a",
        "--border-light": "#5e687c",
        "--green": "#a3be8c",
        "--green-dim": "#1a2416",
        "--amber": "#ebcb8b",
        "--amber-dim": "#2a2416",
        "--red": "#bf616a",
        "--red-dim": "#2a1014",
        "--cyan": "#88c0d0",
        "--cyan-dim": "#14242a",
        "--text": "#e5e9f0",
        "--text-dim": "#6a7a8a",
        "--text-green": "#a3be8c",
        "--progress-from": "#1a2416",
        "--progress-to": "#2a2416",
    },
    "gruvbox": {
        "--bg-primary": "#1d2021",
        "--bg-panel": "#252829",
        "--bg-panel-alt": "#2c2f30",
        "--bg-panel-hi": "#333638",
        "--border": "#3c3f41",
        "--border-light": "#4a4d4f",
        "--green": "#98971a",
        "--green-dim": "#1a1c08",
        "--amber": "#d79921",
        "--amber-dim": "#2a2008",
        "--red": "#cc241d",
        "--red-dim": "#2a0a08",
        "--cyan": "#689d6a",
        "--cyan-dim": "#0e1e10",
        "--text": "#ebdbb2",
        "--text-dim": "#6a5e4a",
        "--text-green": "#98971a",
        "--progress-from": "#1a1c08",
        "--progress-to": "#2a2008",
    },
    "monokai": {
        "--bg-primary": "#1e1f1c",
        "--bg-panel": "#242520",
        "--bg-panel-alt": "#2a2b26",
        "--bg-panel-hi": "#32332e",
        "--border": "#3a3b36",
        "--border-light": "#484946",
        "--green": "#a6e22e",
        "--green-dim": "#182a08",
        "--amber": "#e6db74",
        "--amber-dim": "#2a2814",
        "--red": "#f92672",
        "--red-dim": "#2e0818",
        "--cyan": "#66d9ef",
        "--cyan-dim": "#0a2832",
        "--text": "#f8f8f2",
        "--text-dim": "#6a6a5a",
        "--text-green": "#a6e22e",
        "--progress-from": "#182a08",
        "--progress-to": "#2a2814",
    },
    "catppuccin": {
        "--bg-primary": "#1e1e2e",
        "--bg-panel": "#252538",
        "--bg-panel-alt": "#2b2b40",
        "--bg-panel-hi": "#32324a",
        "--border": "#3a3a52",
        "--border-light": "#484862",
        "--green": "#a6e3a1",
        "--green-dim": "#1a2a18",
        "--amber": "#f9e2af",
        "--amber-dim": "#2a2618",
        "--red": "#f38ba8",
        "--red-dim": "#2e101e",
        "--cyan": "#89dceb",
        "--cyan-dim": "#122a2e",
        "--text": "#cdd6f4",
        "--text-dim": "#5a5a7a",
        "--text-green": "#a6e3a1",
        "--progress-from": "#1a2a18",
        "--progress-to": "#2a2618",
    },
}


def resolve_theme(name: str) -> dict[str, str]:
    """Return the theme dict for *name*, falling back to ``"ifaz"``."""
    return THEMES.get(name, THEMES["ifaz"])


def theme_js(name: str) -> str:
    """Return a JavaScript snippet that applies the named theme in the browser.

    Call ``execute_js()`` on the application window to apply::

        app.execute_js(theme_js("cold"))
    """
    overrides = resolve_theme(name)
    pairs = ",".join(f'"{k}":"{v}"' for k, v in overrides.items())
    return f"iskg_apply_theme({{{pairs}}});"


def theme_css(name: str) -> str:
    """Return a CSS ``:root`` block for the named theme (for initial render)."""
    overrides = resolve_theme(name)
    rules = "".join(f"  {k}: {v};\n" for k, v in overrides.items())
    return f":root {{\n{rules}}}\n"


def available_themes() -> list[str]:
    """Return the list of registered theme names."""
    return list(THEMES.keys())


THEME_VARS: list[str] = [
    "--bg-primary",
    "--bg-panel",
    "--bg-panel-alt",
    "--bg-panel-hi",
    "--border",
    "--border-light",
    "--green",
    "--green-dim",
    "--amber",
    "--amber-dim",
    "--red",
    "--red-dim",
    "--cyan",
    "--cyan-dim",
    "--text",
    "--text-dim",
    "--text-green",
    "--progress-from",
    "--progress-to",
]
