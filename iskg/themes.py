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
    "cold": {
        "--bg-primary": "#060d14",
        "--bg-panel": "#09131f",
        "--bg-panel-alt": "#0e1a28",
        "--bg-panel-hi": "#142335",
        "--border": "#1a2a3e",
        "--border-light": "#253a52",
        "--green": "#38bdf8",
        "--green-dim": "#0a2035",
        "--amber": "#818cf8",
        "--amber-dim": "#1a1a3a",
        "--red": "#f87171",
        "--red-dim": "#2e1018",
        "--cyan": "#67e8f9",
        "--cyan-dim": "#0a2838",
        "--text": "#c8d6e5",
        "--text-dim": "#4a6078",
        "--text-green": "#60a5fa",
        "--progress-from": "#0a2035",
        "--progress-to": "#1a1a3a",
    },
    "warm": {
        "--bg-primary": "#100a06",
        "--bg-panel": "#1a100c",
        "--bg-panel-alt": "#221814",
        "--bg-panel-hi": "#2e2018",
        "--border": "#36281a",
        "--border-light": "#4a3422",
        "--green": "#fb923c",
        "--green-dim": "#2e1a0a",
        "--amber": "#fbbf24",
        "--amber-dim": "#2e2208",
        "--red": "#ef4444",
        "--red-dim": "#2e0e0e",
        "--cyan": "#a78bfa",
        "--cyan-dim": "#1a1030",
        "--text": "#e5d0c8",
        "--text-dim": "#6a5a4a",
        "--text-green": "#fb923c",
        "--progress-from": "#2e1a0a",
        "--progress-to": "#2e2208",
    },
    "night": {
        "--bg-primary": "#030507",
        "--bg-panel": "#06080c",
        "--bg-panel-alt": "#0a0d12",
        "--bg-panel-hi": "#0e121a",
        "--border": "#121820",
        "--border-light": "#1a2230",
        "--green": "#22c55e",
        "--green-dim": "#081a0e",
        "--amber": "#eab308",
        "--amber-dim": "#1a1a06",
        "--red": "#dc2626",
        "--red-dim": "#1a0808",
        "--cyan": "#06b6d4",
        "--cyan-dim": "#061a20",
        "--text": "#8a9aa8",
        "--text-dim": "#3a4a58",
        "--text-green": "#4ade80",
        "--progress-from": "#081a0e",
        "--progress-to": "#1a1a06",
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
    "ocean": {
        "--bg-primary": "#0a0e14",
        "--bg-panel": "#0e141e",
        "--bg-panel-alt": "#121a26",
        "--bg-panel-hi": "#182232",
        "--border": "#1a2a38",
        "--border-light": "#24384a",
        "--green": "#34d399",
        "--green-dim": "#0a1e18",
        "--amber": "#fbbf24",
        "--amber-dim": "#1e1a08",
        "--red": "#f87171",
        "--red-dim": "#2a1212",
        "--cyan": "#22d3ee",
        "--cyan-dim": "#08202e",
        "--text": "#c4d4e0",
        "--text-dim": "#4a6070",
        "--text-green": "#34d399",
        "--progress-from": "#0a1e18",
        "--progress-to": "#1e1a08",
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

# Re-exported for backwards compatibility; applications can also access
# the main IFAZ_CSS from iskg.theme.
# The THEME_VARS list above can be used by tools / IDEs that introspect
# the available theming surface.
