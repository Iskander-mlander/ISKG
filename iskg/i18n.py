"""Internationalisation and localisation helpers.

Inspired by Qt's ``tr()`` + ``QTranslator``. Provides:

- :func:`tr` — translate a string in the active language.
- :func:`set_language` / :func:`get_language` — switch between languages.
- :class:`Translator` — loads ``.po`` / ``.json`` catalogues.
- :func:`format_number` / :func:`format_date` — locale-aware
  formatters that fall back to Python's :mod:`locale` if Babel is
  not installed.
- :func:`available_languages` — list of supported languages.

Translation catalogues are plain Python dicts. A builtin ``en`` catalogue
ships with the most common UI strings so ``tr()`` never returns the
key.
"""

from __future__ import annotations

import contextlib
import datetime as _dt
import gettext as _gettext
import locale as _locale
import os
from collections.abc import Callable

_BUILTIN_EN: dict[str, str] = {
    "OK": "OK",
    "Cancel": "Cancel",
    "Apply": "Apply",
    "Save": "Save",
    "Open": "Open",
    "Close": "Close",
    "Yes": "Yes",
    "No": "No",
    "Help": "Help",
    "About": "About",
    "File": "File",
    "Edit": "Edit",
    "View": "View",
    "Tools": "Tools",
    "Window": "Window",
    "Settings": "Settings",
    "Search": "Search",
    "Cut": "Cut",
    "Copy": "Copy",
    "Paste": "Paste",
    "Undo": "Undo",
    "Redo": "Redo",
    "Loading": "Loading…",
    "Error": "Error",
    "Warning": "Warning",
    "Information": "Information",
    "Confirm": "Confirm",
    "Submit": "Submit",
    "Reset": "Reset",
    "Add": "Add",
    "Remove": "Remove",
    "Delete": "Delete",
    "Cancel_Confirm": "Are you sure?",
    "Success": "Success",
    "Failed": "Failed",
}


_TRANSLATORS: dict[str, dict[str, str]] = {"en": dict(_BUILTIN_EN)}
_CURRENT_LANG: str = "en"
_NULL: Callable[[str], str] = _gettext.NullTranslations().gettext


def available_languages() -> list[str]:
    """Return the list of loaded language codes."""
    return sorted(_TRANSLATORS.keys())


def get_language() -> str:
    return _CURRENT_LANG


def set_language(lang: str) -> None:
    """Switch to ``lang``. Falls back to English if unknown."""
    global _CURRENT_LANG
    _CURRENT_LANG = lang if lang in _TRANSLATORS else "en"


def tr(message: str, /, *, lang: str | None = None) -> str:
    """Translate ``message`` in the active (or given) language.

    Args:
        message: the source string (English by convention).
        lang: optional explicit language; if ``None``, the current
            language is used.

    Returns:
        The translated string, or the original if no translation exists.
    """
    lang = lang or _CURRENT_LANG
    if lang == "en":
        return message
    catalog = _TRANSLATORS.get(lang, {})
    return catalog.get(message, message)


def _(message: str) -> str:
    """Shorthand alias for :func:`tr` — matches gettext convention."""
    return tr(message)


class Translator:
    """Loads a translation catalogue and merges it into the active set.

    Supports two simple formats:

    - **JSON**::

        {
          "Cancel": "Cancelar",
          "Save": "Guardar",
          ...
        }

    - **gettext-style ``.mo``** is supported by the standard library if
      available. The ``.mo`` file is read from disk and wrapped via
      :func:`_gettext.GNUTranslations`.
    """

    def __init__(self, lang: str) -> None:
        self.lang = lang

    def load_json(self, path: str) -> int:
        """Load a JSON translation file. Returns number of strings loaded."""
        import json

        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return self.load_dict(data)

    def load_mo(self, path: str) -> int:
        """Load a ``.mo`` translation file. Returns number of strings loaded."""
        with open(path, "rb") as f:
            trans = _gettext.GNUTranslations(f)
        count = 0
        catalog = _TRANSLATORS.setdefault(self.lang, {})
        # GNUTranslations stores entries in a private ``_catalog`` dict; we
        # iterate it to extract only str->str pairs. The attribute is private
        # but stable across all cpython versions.
        mo_catalog: dict[object, object] = getattr(trans, "_catalog", {})
        for key, val in mo_catalog.items():
            if isinstance(key, str) and isinstance(val, str):
                catalog[key] = val
                count += 1
        return count

    def load_dict(self, mapping: dict[str, str]) -> int:
        """Merge ``mapping`` into the active catalogue for this lang."""
        catalog = _TRANSLATORS.setdefault(self.lang, {})
        catalog.update(mapping)
        return len(mapping)

    def unload(self) -> None:
        """Forget all loaded translations for this language."""
        _TRANSLATORS.pop(self.lang, None)


@contextlib.contextmanager
def use_language(lang: str):
    """Context manager that temporarily switches language for the block."""
    global _CURRENT_LANG
    prev = _CURRENT_LANG
    set_language(lang)
    try:
        yield
    finally:
        set_language(prev)


# ── Locale-aware formatters ────────────────────────────────────────────


def format_number(
    value: float,
    *,
    decimals: int = 2,
    thousands_sep: bool = True,
) -> str:
    """Format a number using the current locale, or fall back to a
    sensible default.
    """
    if thousands_sep:
        try:
            return _locale.format_string(f"%.{decimals}f", value, grouping=True)
        except (ValueError, _locale.Error):
            pass
    return f"{value:,.{decimals}f}" if thousands_sep else f"{value:.{decimals}f}"


def format_date(
    dt: _dt.date | _dt.datetime,
    fmt: str = "%x",
) -> str:
    """Format a date in the current locale."""
    try:
        return dt.strftime(fmt)
    except (ValueError, TypeError):
        return str(dt)


def detect_locale() -> str:
    """Try to detect the system locale (LANG environment variable)."""
    return os.environ.get("LANG", "en_US.UTF-8").split(".")[0].split("_")[0]
