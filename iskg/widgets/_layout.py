from __future__ import annotations

from typing import Any

from ..base import _LAYOUT_STACK
from ._containers import Frame, Separator, Spacer
from ._controls import Button, ComboBox, Entry
from ._data import TreeView
from ._display import Label
from ._logview import LogViewer
from ._text import Text


class Box(Frame):
    """Auto-flowing container that removes per-widget ``grid``/``columnconfigure``
    boilerplate.

    Children added via :meth:`add` or the ``button``/``label``/... shorthand
    creators are packed automatically along ``direction`` with a default ``gap``
    and padding. In a vertical box children stretch to fill the width
    (``fill="x"``); pass ``fill``/``expand`` to override per child.

    Boxes also work as context managers for a declarative, indentation-based
    layout. Inside a ``with`` block, any widget created without an explicit
    ``parent`` is auto-parented (and auto-packed) into the active box::

        with VBox(gap=8) as root:
            root.label("Hola")
            with HBox(gap=6):
                Button("A")
                Button("B")
    """

    def __init__(
        self,
        parent: Any = None,
        direction: str = "vertical",
        gap: int = 6,
        padx: int = 4,
        pady: int = 4,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._box_dir = "horizontal" if direction in ("h", "row", "horizontal") else "vertical"
        self._box_padx = padx
        self._box_pady = pady
        self.config(gap=gap)

    def __enter__(self) -> Box:
        _LAYOUT_STACK.append(self)
        return self

    def __exit__(self, *exc: Any) -> bool:
        if _LAYOUT_STACK and _LAYOUT_STACK[-1] is self:
            _LAYOUT_STACK.pop()
        return False

    def add(
        self, child: Any, padx=None, pady=None, fill=None, expand: bool = False, **kwargs: Any
    ) -> Any:
        if child not in self._children:
            super().add(child)
        side = "left" if self._box_dir == "horizontal" else "top"
        if fill is None:
            fill = "x" if self._box_dir != "horizontal" else "none"
        child.pack(
            side=side,
            padx=padx if padx is not None else self._box_padx,
            pady=pady if pady is not None else self._box_pady,
            fill=fill,
            expand=expand,
            **kwargs,
        )
        return child

    def spacer(self, expand: bool = True, **kwargs: Any) -> Any:
        return self.add(Spacer(expand=expand, **kwargs))

    def spring(self, expand: bool = True, **kwargs: Any) -> Any:
        return self.add(Spacer(expand=expand, **kwargs))

    def sep(self, orient: str | None = None, **kwargs: Any) -> Any:
        o = orient or ("vertical" if self._box_dir == "horizontal" else "horizontal")
        return self.add(Separator(orient=o, **kwargs))

    def button(self, text: str = "", **kwargs: Any) -> Any:
        return Button(parent=self, text=text, **kwargs)

    def label(self, text: str = "", **kwargs: Any) -> Any:
        return Label(parent=self, text=text, **kwargs)

    def entry(self, text: str = "", **kwargs: Any) -> Any:
        return Entry(parent=self, text=text, **kwargs)

    def combo(self, values=None, **kwargs: Any) -> Any:
        return ComboBox(parent=self, values=values or [], **kwargs)

    def textbox(self, **kwargs: Any) -> Any:
        return Text(parent=self, **kwargs)

    def tree(self, **kwargs: Any) -> Any:
        return TreeView(parent=self, **kwargs)

    def logview(self, **kwargs: Any) -> Any:
        return LogViewer(parent=self, **kwargs)


class HBox(Box):
    """Horizontal :class:`Box` — children flow left-to-right."""

    def __init__(self, parent: Any = None, **kwargs: Any) -> None:
        super().__init__(parent, direction="horizontal", **kwargs)


class VBox(Box):
    """Vertical :class:`Box` — children flow top-to-bottom (the default)."""

    def __init__(self, parent: Any = None, **kwargs: Any) -> None:
        super().__init__(parent, direction="vertical", **kwargs)
