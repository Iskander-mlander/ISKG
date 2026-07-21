from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Variable:
    """Base variable class for data binding (tkinter ``Variable`` pattern).

    Subclasses: :class:`StringVar`, :class:`IntVar`, :class:`DoubleVar`,
    :class:`BooleanVar`.
    """

    def __init__(self, value: Any = None) -> None:
        self._value = value
        self._traces: list[tuple[str, Callable]] = []
        self._widgets: list[Any] = []

    def set(self, value: Any, _from_widget: Any = None) -> None:
        """Set the variable value and notify observers.

        Args:
            value: new value (type-coerced by subclasses).
            _from_widget: widget that triggered the change (prevents echo).
        """
        self._value = value
        for mode, cb in self._traces:
            if mode == "write":
                cb(None, None, "write")
        for w in self._widgets:
            if w is not _from_widget:
                w._var_updated(self)

    def get(self) -> Any:
        """Return the current value."""
        return self._value

    def trace_add(self, mode: str, callback: Callable) -> None:
        """Register a trace callback (``mode`` can be ``"write"``, ``"read"``, ``"unset"``)."""
        self._traces.append((mode, callback))

    def trace_remove(self, mode: str, callback: Callable) -> None:
        """Remove a previously registered trace."""
        self._traces = [(m, c) for m, c in self._traces if not (m == mode and c == callback)]


class StringVar(Variable):
    """Variable holding a ``str``."""

    def __init__(self, value: str = "") -> None:
        super().__init__(str(value))

    def set(self, value: Any, _from_widget: Any = None) -> None:
        super().set(str(value), _from_widget)

    def get(self) -> str:
        v = super().get()
        return str(v) if v is not None else ""


class IntVar(Variable):
    """Variable holding an ``int``."""

    def __init__(self, value: int = 0) -> None:
        super().__init__(int(value))

    def set(self, value: Any, _from_widget: Any = None) -> None:
        super().set(int(value), _from_widget)

    def get(self) -> int:
        v = super().get()
        return int(v) if v is not None else 0


class DoubleVar(Variable):
    """Variable holding a ``float``."""

    def __init__(self, value: float = 0.0) -> None:
        super().__init__(float(value))

    def set(self, value: Any, _from_widget: Any = None) -> None:
        super().set(float(value), _from_widget)

    def get(self) -> float:
        v = super().get()
        return float(v) if v is not None else 0.0


class BooleanVar(Variable):
    """Variable holding a ``bool``."""

    def __init__(self, value: bool = False) -> None:
        super().__init__(bool(value))

    def set(self, value: Any, _from_widget: Any = None) -> None:
        if isinstance(value, str):
            value = value.lower() == "true"
        super().set(bool(value), _from_widget)

    def get(self) -> bool:
        v = super().get()
        return bool(v) if v is not None else False
