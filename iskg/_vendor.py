from __future__ import annotations

import os
import subprocess
import sys

_VENDOR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "_vendor")


def _ensure_vendor_dir() -> str:
    os.makedirs(_VENDOR_DIR, exist_ok=True)
    return _VENDOR_DIR


def try_import(module: str, package: str = "") -> None:
    """Import *module*, auto-installing it locally if missing.

    Installs into ``_vendor/`` at project root so the project remains
    self-contained (portable). Only pure-Python wheels are guaranteed;
    platform-native dependencies (GTK, WebKit) must be pre-installed.
    """
    try:
        __import__(module)
        return
    except ImportError:
        pass

    pkg = package or module
    vendor = _ensure_vendor_dir()

    if vendor not in sys.path:
        sys.path.insert(0, vendor)

    # Check again after adding to path
    try:
        __import__(module)
        return
    except ImportError:
        pass

    print(f"ISKG: Installing {pkg} locally...")
    try:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--target",
                vendor,
                pkg,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        print(
            f"ISKG: Failed to install {pkg}. Try: pip install {pkg}\nError: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"ISKG: {pkg} installed locally.")
    __import__(module)
