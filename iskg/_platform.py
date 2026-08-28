"""Cross-platform helpers for ISKG.

Centralises:

* OS detection (Windows / macOS / Linux / BSD) and family (Win/Mac/Posix).
* User paths: config dir, data dir, cache dir, scaffold templates dir.
* Filesystem helpers safe on every platform.

This module imports nothing heavy and is safe to import at the very start
of the CLI bootstrap (it must not pull in pywebview, GTK, or any webview
backend).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Final

IS_WINDOWS: Final = sys.platform == "win32" or sys.platform.startswith("cygwin")
IS_MACOS: Final = sys.platform == "darwin"
IS_LINUX: Final = sys.platform.startswith("linux")
IS_BSD: Final = sys.platform.startswith(("freebsd", "openbsd", "netbsd"))
IS_POSIX: Final = not IS_WINDOWS

OS_NAME: Final = (
    "windows"
    if IS_WINDOWS
    else "macos"
    if IS_MACOS
    else "linux"
    if IS_LINUX
    else "bsd"
    if IS_BSD
    else sys.platform
)


def _app_dir() -> str:
    return "ISKG"


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def user_config_dir() -> Path:
    """Per-user configuration directory.

    * Windows: ``%APPDATA%\\ISKG`` (falls back to ``~/ISKG``).
    * macOS:   ``~/Library/Application Support/ISKG``.
    * Linux:   ``$XDG_CONFIG_HOME/iskg`` or ``~/.config/iskg``.
    """
    if IS_WINDOWS:
        base = os.environ.get("APPDATA") or str(Path.home() / _app_dir())
        return _ensure_dir(Path(base) / _app_dir())
    if IS_MACOS:
        return _ensure_dir(Path.home() / "Library" / "Application Support" / _app_dir())
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return _ensure_dir(Path(base) / "iskg")


def user_data_dir() -> Path:
    """Per-user data directory (project-local state, logs, etc.)."""
    if IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if not base:
            base = str(Path.home() / _app_dir())
        return _ensure_dir(Path(base) / _app_dir() / "data")
    if IS_MACOS:
        return _ensure_dir(Path.home() / "Library" / "Application Support" / _app_dir() / "data")
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return _ensure_dir(Path(base) / "iskg")


def user_cache_dir() -> Path:
    """Per-user cache directory (compiled templates, etc.)."""
    if IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / _app_dir())
        return _ensure_dir(Path(base) / _app_dir() / "cache")
    if IS_MACOS:
        return _ensure_dir(Path.home() / "Library" / "Caches" / _app_dir())
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return _ensure_dir(Path(base) / "iskg")


def scaffold_templates_dir() -> Path:
    """Where the bundled ``iskg new <template>`` scaffolds live.

    Located inside the installed package and read-only at runtime.
    """
    return Path(__file__).resolve().parent / "scaffolds"


def native_line_ending(text: str) -> str:
    """Normalise line endings for the current platform (mainly Windows)."""
    if IS_WINDOWS:
        return text.replace("\r\n", "\n").replace("\n", "\r\n")
    return text.replace("\r\n", "\n")


def path_separator() -> str:
    return ";" if IS_WINDOWS else ":"


def which(cmd: str) -> str | None:
    """``shutil.which`` re-exported here so callers don't have to import shutil."""
    import shutil

    return shutil.which(cmd)


__all__ = [
    "IS_WINDOWS",
    "IS_MACOS",
    "IS_LINUX",
    "IS_BSD",
    "IS_POSIX",
    "OS_NAME",
    "user_config_dir",
    "user_data_dir",
    "user_cache_dir",
    "scaffold_templates_dir",
    "native_line_ending",
    "path_separator",
    "which",
]
