"""Form validation system (QValidator-style + HTML5 form validation patterns).

Provides:

- :class:`Validator`: abstract base class for all validators.
- Concrete validators: :class:`RequiredValidator`, :class:`RangeValidator`,
  :class:`PatternValidator`, :class:`LengthValidator`,
  :class:`EmailValidator`, :class:`URLValidator`, :class:`NumberValidator`,
  :class:`CustomValidator`.
- :class:`Form`: groups widgets and runs all attached validators.
- :class:`FieldState`: an enum of intermediate validation states (Qt-style).

Validators are attached to widgets and emit ``"valid"`` / ``"invalid"``
events. :class:`Form` aggregates per-widget state and exposes a single
``is_valid`` property plus per-field error messages.

The visual feedback (red border, error label) is rendered via a
``validation`` CSS class injected on the widget element, so no widget
code needs to know about validation.
"""

from __future__ import annotations

import contextlib
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class FieldState(Enum):
    """Qt-like validation state."""

    Acceptable = "acceptable"
    Intermediate = "intermediate"
    Invalid = "invalid"


@dataclass
class ValidationResult:
    """Result of a validation pass."""

    state: FieldState
    message: str = ""

    @property
    def is_valid(self) -> bool:
        return self.state == FieldState.Acceptable

    @property
    def is_invalid(self) -> bool:
        return self.state == FieldState.Invalid


class Validator(ABC):
    """Abstract base class for all field validators.

    A validator inspects a widget's current value and returns a
    :class:`ValidationResult`. The ``target`` is the widget to validate;
    its ``.text`` / ``.value`` / ``.checked`` etc. attributes are read
    depending on the validator's expectations.
    """

    def __init__(self, message: str = "") -> None:
        self._message = message
        self._widget: Any = None

    def attach(self, widget: Any) -> Validator:
        """Attach this validator to a widget and return ``self``."""
        self._widget = widget
        self._apply_visual(ValidationResult(FieldState.Acceptable, ""))
        return self

    def detach(self) -> None:
        self._widget = None
        self._apply_visual(ValidationResult(FieldState.Acceptable, ""))

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Inspect ``value`` and return a :class:`ValidationResult`."""

    def check(self) -> ValidationResult:
        """Run :meth:`validate` against the attached widget's value."""
        if self._widget is None:
            return ValidationResult(FieldState.Acceptable, "")
        value = self._extract_value(self._widget)
        result = self.validate(value)
        self._apply_visual(result)
        return result

    def _extract_value(self, widget: Any) -> Any:
        for attr in ("text", "value", "checked"):
            if hasattr(widget, attr):
                v = getattr(widget, attr)
                if not callable(v):
                    return v
        return None

    def _apply_visual(self, result: ValidationResult) -> None:
        """Update the widget's CSS class to reflect the result."""
        w = self._widget
        if w is None:
            return
        w._config_dict["validation_state"] = result.state.value
        w._config_dict["validation_message"] = result.message
        # Force a CSS class refresh by appending/clearing the marker.
        if result.state == FieldState.Invalid:
            w._config_dict["invalid"] = True
        else:
            w._config_dict.pop("invalid", None)
        with contextlib.suppress(Exception):
            w._sync()


class RequiredValidator(Validator):
    """Ensure the field has a non-empty value."""

    def __init__(self, message: str = "This field is required") -> None:
        super().__init__(message)

    def validate(self, value: Any) -> ValidationResult:
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationResult(FieldState.Invalid, self._message)
        return ValidationResult(FieldState.Acceptable, "")


class RangeValidator(Validator):
    """Constrain a numeric value to ``[min_val, max_val]``."""

    def __init__(
        self,
        min_val: float | None = None,
        max_val: float | None = None,
        message: str = "Value out of range",
    ) -> None:
        super().__init__(message)
        self._min = min_val
        self._max = max_val

    def validate(self, value: Any) -> ValidationResult:
        if value is None or value == "":
            return ValidationResult(FieldState.Intermediate, "")
        try:
            num = float(value)
        except (TypeError, ValueError):
            return ValidationResult(FieldState.Invalid, f"{self._message} (not a number)")
        if self._min is not None and num < self._min:
            return ValidationResult(FieldState.Invalid, f"{self._message} (min: {self._min})")
        if self._max is not None and num > self._max:
            return ValidationResult(FieldState.Invalid, f"{self._message} (max: {self._max})")
        return ValidationResult(FieldState.Acceptable, "")


class LengthValidator(Validator):
    """Constrain a string's length to ``[min_len, max_len]``."""

    def __init__(
        self,
        min_len: int | None = None,
        max_len: int | None = None,
        message: str = "Length out of range",
    ) -> None:
        super().__init__(message)
        self._min_len = min_len
        self._max_len = max_len

    def validate(self, value: Any) -> ValidationResult:
        if value is None:
            return ValidationResult(FieldState.Intermediate, "")
        s = str(value)
        n = len(s)
        if self._min_len is not None and n < self._min_len:
            return ValidationResult(FieldState.Invalid, f"{self._message} (min: {self._min_len})")
        if self._max_len is not None and n > self._max_len:
            return ValidationResult(FieldState.Invalid, f"{self._message} (max: {self._max_len})")
        return ValidationResult(FieldState.Acceptable, "")


class PatternValidator(Validator):
    """Match ``value`` against a regular expression."""

    def __init__(self, pattern: str, message: str = "Invalid format") -> None:
        super().__init__(message)
        self._re = re.compile(pattern)

    def validate(self, value: Any) -> ValidationResult:
        if value is None or value == "":
            return ValidationResult(FieldState.Intermediate, "")
        if not self._re.search(str(value)):
            return ValidationResult(FieldState.Invalid, self._message)
        return ValidationResult(FieldState.Acceptable, "")


class EmailValidator(PatternValidator):
    """Validate RFC-5321-ish email addresses (simplified)."""

    def __init__(self, message: str = "Invalid email") -> None:
        super().__init__(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message)


class URLValidator(PatternValidator):
    """Validate http/https URLs."""

    def __init__(self, message: str = "Invalid URL") -> None:
        super().__init__(r"^https?://[^\s/$.?#].[^\s]*$", message)


class NumberValidator(PatternValidator):
    """Validate that the value is a well-formed number."""

    def __init__(self, message: str = "Not a number") -> None:
        super().__init__(r"^-?\d+(\.\d+)?$", message)


class CustomValidator(Validator):
    """Wrap any callable ``(value) -> bool`` as a validator."""

    def __init__(
        self,
        fn: Callable[[Any], bool],
        message: str = "Validation failed",
    ) -> None:
        super().__init__(message)
        self._fn = fn

    def validate(self, value: Any) -> ValidationResult:
        if value is None or value == "":
            return ValidationResult(FieldState.Intermediate, "")
        try:
            ok = bool(self._fn(value))
        except Exception as exc:  # noqa: BLE001
            return ValidationResult(FieldState.Invalid, f"{self._message}: {exc}")
        return (
            ValidationResult(FieldState.Acceptable, "")
            if ok
            else ValidationResult(FieldState.Invalid, self._message)
        )


class Form:
    """Aggregate a set of widget+validator pairs and run them all.

    Usage::

        form = Form()
        form.add_field(name_input, RequiredValidator())
        form.add_field(email_input, EmailValidator())
        form.add_field(age_input, RangeValidator(0, 120))
        if form.is_valid:
            submit(form.collect())
    """

    def __init__(self) -> None:
        self._fields: list[tuple[Any, Validator]] = []
        self._on_change: Callable[[Form], None] | None = None

    def add_field(
        self,
        widget: Any,
        validator: Validator | list[Validator],
    ) -> Form:
        """Attach ``widget`` with one or more :class:`Validator` instances."""
        if isinstance(validator, list):
            for v in validator:
                v.attach(widget)
                self._fields.append((widget, v))
        else:
            validator.attach(widget)
            self._fields.append((widget, validator))
        return self

    def remove_field(self, widget: Any) -> None:
        self._fields = [(w, v) for w, v in self._fields if w is not widget]
        for w, v in self._fields:
            if w is widget:
                v.detach()

    def on_change(self, callback: Callable[[Form], None]) -> None:
        """Register a callback fired whenever :meth:`validate_all` runs."""
        self._on_change = callback

    def validate_all(self) -> bool:
        """Run all validators. Returns ``True`` if every field is valid."""
        all_ok = True
        for _, v in self._fields:
            res = v.check()
            if not res.is_valid:
                all_ok = False
        if self._on_change is not None:
            with contextlib.suppress(Exception):
                self._on_change(self)
        return all_ok

    @property
    def is_valid(self) -> bool:
        """``True`` if every attached validator is currently passing."""
        return all(v.check().is_valid for _, v in self._fields)

    @property
    def errors(self) -> dict[int, str]:
        """Map widget-id to error message for every invalid field."""
        out: dict[int, str] = {}
        for w, v in self._fields:
            res = v.check()
            if not res.is_valid:
                out[id(w)] = res.message
        return out

    def collect(self) -> dict[str, Any]:
        """Return a dict ``{attr_name: value}`` for each registered widget.

        Widgets are stored in ``self._fields`` in registration order. The
        attr name defaults to ``widget._id`` but can be overridden by
        setting ``widget._form_attr = "name"`` before adding.
        """
        out: dict[str, Any] = {}
        for w, _ in self._fields:
            attr = getattr(w, "_form_attr", None) or w._id
            for prop in ("text", "value", "checked"):
                if hasattr(w, prop):
                    v = getattr(w, prop)
                    if not callable(v):
                        out[attr] = v
                        break
        return out
