"""Default visual metrics for ISKG widgets.

Single source of truth for the comfortable UI scale. The CSS theme
(``iskg/themes/ifaz.css``) and the content-minimum propagation
(:meth:`iskg.base.Widget._content_min_size`) both follow these values,
so a widget is never rendered — or squeezed — below them unless the
code opts out explicitly (``fit=False``, or explicit
``width``/``height``/``min_width``/``min_height``).

Note: ``ImageBox(fit=...)`` uses the name ``fit`` for its own image
scaling mode (a string like ``"contain"``); the content-minimum
``fit`` flag is a boolean and only interpreted as opt-out when
strictly ``False``.
"""

BUTTON_HEIGHT = 30
BUTTON_FONT_SIZE = 12
BUTTON_PAD_X = 16
BUTTON_LETTER_SPACING = 1
BUTTON_BORDER = 2

BUTTON_SM_HEIGHT = 24
BUTTON_SM_FONT_SIZE = 11
BUTTON_SM_PAD_X = 12
BUTTON_SM_LETTER_SPACING = 0.5

BUTTON_LG_HEIGHT = 36
BUTTON_LG_FONT_SIZE = 14
BUTTON_LG_PAD_X = 20
BUTTON_LG_LETTER_SPACING = 1

BUTTON_TINY_HEIGHT = 18
BUTTON_TINY_FONT_SIZE = 8
BUTTON_TINY_PAD_X = 6
BUTTON_TINY_LETTER_SPACING = 0.5

ENTRY_HEIGHT = 28
ENTRY_WIDTH = 150
ENTRY_FONT_SIZE = 12
ENTRY_PAD_X = 10
ENTRY_BORDER = 2

LABEL_FONT_SIZE = 11
LABEL_LINE_HEIGHT = 17
LABEL_HEIGHT = 20
LABEL_PAD_X = 2

CHECK_HEIGHT = 22
CHECK_BOX = 16
CHECK_GAP = 6
CHECK_PAD_X = 6
CHECK_FONT_SIZE = 11

NOTEBOOK_TABBAR_HEIGHT = 28

FRAME_PADDING = 6
FRAME_BORDER = 1
FRAME_HEADER_HEIGHT = 20

CHAR_WIDTH_FACTOR = 0.62


def char_width(font_size: float) -> float:
    """Approximate advance width of one character in the mono UI font."""
    return font_size * CHAR_WIDTH_FACTOR


def estimate_text_width(
    text: object,
    font_size: float = LABEL_FONT_SIZE,
    pad_x: int = 0,
    letter_spacing: float = 0,
    extra: int = 0,
) -> int:
    """Estimate the pixel width of ``text`` in the mono UI font.

    Uses the longest line (labels/buttons do not wrap their minimum).
    Crude by design — it only feeds minimum-size propagation, and any
    explicit ``width``/``min_width`` set in code wins over the estimate.
    """
    lines = str(text if text is not None else "").splitlines() or [""]
    longest = max(len(ln) for ln in lines)
    return int(longest * (char_width(font_size) + letter_spacing)) + 2 * pad_x + extra
