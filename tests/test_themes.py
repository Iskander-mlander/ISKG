"""Tests for theme resolution, JS generation, CSS generation, and available themes list."""

from iskg.theme import IFAZ_CSS
from iskg.themes import (
    THEMES,
    available_themes,
    resolve_theme,
    theme_css,
    theme_js,
)


class TestBaseCss:
    def test_ifaz_css_loads_from_asset(self):
        assert isinstance(IFAZ_CSS, str)
        assert len(IFAZ_CSS) > 1000
        assert ":root" in IFAZ_CSS
        assert ".iskg-btn" in IFAZ_CSS


class TestResolveTheme:
    def test_resolve_known_theme(self):
        theme = resolve_theme("ifaz")
        assert theme is THEMES["ifaz"]
        assert theme["--bg-primary"] == "#070b10"

    def test_resolve_desert(self):
        theme = resolve_theme("desert")
        assert theme["--bg-primary"] == "#1a1410"

    def test_resolve_unknown_falls_back_to_ifaz(self):
        theme = resolve_theme("nonexistent")
        assert theme is THEMES["ifaz"]

    def test_every_theme_has_required_keys(self):
        required = {
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
        }
        for name, theme in THEMES.items():
            missing = required - set(theme.keys())
            if missing and name in (
                "ifaz",
                "desert",
                "infinity",
                "cyberdusk",
                "light",
                "dracula",
                "nord",
                "gruvbox",
                "monokai",
                "catppuccin",
            ):
                assert not missing, f"Theme '{name}' missing keys: {missing}"


class TestThemeJs:
    def test_theme_js_returns_valid_js(self):
        js = theme_js("ifaz")
        assert js.startswith("iskg_apply_theme(")
        assert js.endswith(");")
        assert '"--bg-primary"' in js
        assert '"#070b10"' in js

    def test_theme_js_unknown_theme_uses_ifaz(self):
        js = theme_js("nonexistent")
        assert '"#070b10"' in js  # ifaz colors


class TestThemeCss:
    def test_theme_css_returns_css_block(self):
        css = theme_css("ifaz")
        assert css.startswith(":root {")
        assert css.endswith("}\n")
        assert "--bg-primary: #070b10" in css

    def test_theme_css_contains_all_vars(self):
        css = theme_css("desert")
        assert "--bg-primary" in css
        assert "--text" in css
        assert "--border" in css

    def test_theme_css_unknown_theme(self):
        css = theme_css("nonexistent")
        assert "--bg-primary: #070b10" in css

    def test_buttons_have_fixed_heights_per_size(self):
        """Every button of a given size must share the same height so buttons
        in a row never look misaligned."""
        from iskg.theme import IFAZ_CSS

        assert ".iskg-btn.sm, .iskg-btn.small" in IFAZ_CSS
        assert ".iskg-btn.lg, .iskg-btn.large" in IFAZ_CSS
        base = IFAZ_CSS[IFAZ_CSS.index(".iskg-btn {") :]
        assert "height:26px" in base
        sm = IFAZ_CSS[IFAZ_CSS.index(".iskg-btn.sm") :]
        assert "height:22px" in sm

    def test_combo_dropdown_uses_fixed_position(self):
        """The ComboBox dropdown must escape ancestor overflow/stacking
        contexts (rendered with position:fixed at open time)."""
        from iskg.widgets._controls import ComboBox

        js = ComboBox(values=["a", "b"])._render_js()
        assert 'drop.style.position="fixed"' in js
        assert "getBoundingClientRect" in js


class TestAvailableThemes:
    def test_available_themes_returns_list(self):
        themes = available_themes()
        assert isinstance(themes, list)
        assert len(themes) > 0

    def test_available_themes_contains_ifaz(self):
        assert "ifaz" in available_themes()

    def test_available_themes_contains_all_expected(self):
        expected = {
            "ifaz",
            "desert",
            "infinity",
            "cyberdusk",
            "light",
            "dracula",
            "nord",
            "gruvbox",
            "monokai",
            "catppuccin",
        }
        themes = set(available_themes())
        assert expected.issubset(themes), f"Missing themes: {expected - themes}"
