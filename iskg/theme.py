"""Base IFAZ style sheet for ISKG.

The CSS lives in ``iskg/themes/ifaz.css`` (loaded at import time) so it can be
edited as a real stylesheet instead of a giant Python string. Named-theme
overrides (CSS custom properties) are defined in :mod:`iskg.themes`.
"""

from importlib import resources

IFAZ_CSS: str = (resources.files("iskg") / "themes" / "ifaz.css").read_text(encoding="utf-8")
