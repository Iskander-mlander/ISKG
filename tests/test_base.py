"""Tests for iskg.base — Widget base class and layout engines."""

from unittest.mock import Mock, patch

import pytest

from iskg.base import Widget, _new_id, _validate_css_value

# ── Helper: concrete widget for testing ─────────────────────────────


class _ConcreteWidget(Widget):
    """Minimal concrete Widget subclass for testing (no extra rendering)."""


class _WidgetWithRender(_ConcreteWidget):
    def _render(self) -> str:
        style = self._render_style()
        if self._layout_mode in ("grid", "pack"):
            return f'<div id="{self._id}" style="{style}"></div>'
        return f'<span id="{self._id}" style="{style}">text</span>'


class _WidgetWithUpdateJs(_ConcreteWidget):
    def _render_update_js(self) -> str:
        return "custom_update_js();"


# ── _new_id / _validate_css_value ───────────────────────────────────


def test_new_id_increments():
    ids = {_new_id() for _ in range(5)}
    assert len(ids) == 5
    assert all(i.startswith("iw") for i in ids)


def test_validate_css_value_px_key_string_no_digits():
    with pytest.warns(UserWarning, match="Numeric CSS key"):
        _validate_css_value("padding", "px")  # no digits → warns


def test_validate_css_value_px_key_none():
    _validate_css_value("padding", None)  # no warn


def test_validate_css_value_px_key_number():
    _validate_css_value("padding", 10)  # no warn


def test_validate_css_value_non_px_key():
    _validate_css_value("bg", "red")  # no warn


# ── Widget.__init__ ──────────────────────────────────────────────────


class TestWidgetInit:
    def test_creates_id(self):
        w = _ConcreteWidget()
        assert w._id.startswith("iw")

    def test_default_attributes(self):
        w = _ConcreteWidget()
        assert w._parent is None
        assert w._children == []
        assert w._config_dict == {}
        assert w._layout_mode is None
        assert w._layout_info == {}
        assert w._destroyed is False

    def test_parent_adds_child(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        assert child._parent is parent
        assert child in parent._children

    def test_config_state(self):
        w = _ConcreteWidget(state="disabled")
        assert w._config_dict["state"] == "disabled"
        assert w._config_dict["disabled"] is True

    def test_config_font_string(self):
        w = _ConcreteWidget(font="16px Arial")
        assert w._config_dict["font"] == "16px Arial"

    def test_config_font_tuple(self):
        w = _ConcreteWidget(font=("Helvetica", 14, "bold"))
        assert w._config_dict.get("font-family") == "Helvetica"
        assert w._config_dict.get("font-size") == 14
        assert w._config_dict.get("font-weight") == "bold"

    def test_config_textvariable(self):
        mock_var = Mock()
        mock_var._widgets = []
        w = _ConcreteWidget(textvariable=mock_var)
        assert w._textvariable is mock_var
        assert w in mock_var._widgets

    def test_config_textvariable_none(self):
        w = _ConcreteWidget(textvariable=None)
        assert w._textvariable is None

    def test_config_variable(self):
        mock_var = Mock()
        mock_var._widgets = []
        w = _ConcreteWidget(variable=mock_var)
        assert w._variable is mock_var
        assert w in mock_var._widgets

    def test_config_tooltip(self):
        w = _ConcreteWidget(tooltip="Help text")
        assert w._config_dict["tooltip"] == "Help text"

    def test_config_generic(self):
        w = _ConcreteWidget(padding=10, bg="red")
        assert w._config_dict["padding"] == 10

    def test_type_validation_raises_on_init(self):
        with pytest.raises(TypeError):
            _ConcreteWidget(visible="yes")

    def test_type_validation_passes_valid(self):
        _ConcreteWidget(visible=True, text="hi", width=100)

    def test_type_validation_accepts_none(self):
        _ConcreteWidget(visible=None, text=None, width=None)

    def test_type_validation_unknown_key_skipped(self):
        _ConcreteWidget(some_unknown_key="any value")

    def test_underscore_to_hyphen(self):
        w = _ConcreteWidget(font_size=18)
        assert w._config_dict.get("font-size") == 18


# ── Properties: app, parent, widget_id ──────────────────────────────


class TestWidgetProperties:
    def test_widget_id(self):
        w = _ConcreteWidget()
        assert w.widget_id == w._id

    def test_parent_property(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        assert child.parent is parent

    def test_parent_none(self):
        w = _ConcreteWidget()
        assert w.parent is None

    def test_app_none(self):
        w = _ConcreteWidget()
        assert w.app is None

    def test_app_from_parent(self):
        parent = _ConcreteWidget()
        parent._app = "app_instance"
        child = _ConcreteWidget(parent=parent)
        assert child.app == "app_instance"

    def test_app_direct(self):
        w = _ConcreteWidget()
        w._app = "app_instance"
        assert w.app == "app_instance"


# ── add / remove children ────────────────────────────────────────────


class TestAddRemove:
    def test_add_sets_parent(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget()
        parent.add(child)
        assert child._parent is parent
        assert child in parent._children

    def test_add_idempotent(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget()
        parent.add(child)
        parent.add(child)  # second add — no-op
        assert len(parent._children) == 1

    def test_add_with_app_registers_handler(self):
        parent = _ConcreteWidget()
        parent._app = Mock()
        parent._app._running = True
        child = _ConcreteWidget()
        with patch("iskg.app._HANDLERS", {}):
            parent.add(child)
            assert child._app is parent._app

    def test_remove_removes_parent(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget()
        parent.add(child)
        parent.remove(child)
        assert child._parent is None
        assert child not in parent._children

    def test_remove_not_present(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget()
        parent.remove(child)  # should not raise


# ── pack ─────────────────────────────────────────────────────────────


class TestPack:
    def test_pack_defaults(self):
        w = _ConcreteWidget()
        w.pack()
        assert w._layout_mode == "pack"
        assert w._layout_info["side"] == "top"
        assert w._layout_info["fill"] == "none"
        assert w._layout_info["expand"] is False

    def test_pack_custom(self):
        w = _ConcreteWidget()
        w.pack(side="left", fill="x", expand=True, padx=5, pady=10, anchor="center")
        assert w._layout_info["side"] == "left"
        assert w._layout_info["fill"] == "x"
        assert w._layout_info["expand"] is True
        assert w._layout_info["padx"] == 5
        assert w._layout_info["pady"] == 10

    def test_pack_reparents(self):
        parent1 = _ConcreteWidget()
        parent2 = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent1)
        child.pack(in_=parent2)
        assert child._parent is parent2
        assert child not in parent1._children

    def test_pack_warns_layout_mismatch(self):
        w = _ConcreteWidget()
        w.grid()  # first layout
        with pytest.warns(UserWarning, match="pack.*grid"):
            w.pack()

    def test_pack_removes_hidden(self):
        w = _ConcreteWidget()
        w._config_dict["hidden"] = True
        w.pack()
        assert "hidden" not in w._config_dict

    def test_pack_returns_self(self):
        w = _ConcreteWidget()
        assert w.pack() is w


# ── grid ─────────────────────────────────────────────────────────────


class TestGrid:
    def test_grid_defaults(self):
        w = _ConcreteWidget()
        w.grid()
        assert w._layout_mode == "grid"
        assert w._layout_info["row"] == 0
        assert w._layout_info["column"] == 0
        assert w._layout_info["sticky"] == ""

    def test_grid_custom(self):
        w = _ConcreteWidget()
        w.grid(row=2, column=3, rowspan=2, columnspan=3, sticky="nsew", padx=4, pady=5)
        assert w._layout_info["row"] == 2
        assert w._layout_info["column"] == 3
        assert w._layout_info["rowspan"] == 2
        assert w._layout_info["columnspan"] == 3
        assert w._layout_info["sticky"] == "nsew"

    def test_grid_warns_mismatch(self):
        w = _ConcreteWidget()
        w.pack()
        with pytest.warns(UserWarning, match="grid.*pack"):
            w.grid()

    def test_grid_removes_hidden_and_saved(self):
        w = _ConcreteWidget()
        w._config_dict["hidden"] = True
        w._config_dict["_grid_saved"] = {"row": 0}
        w.grid()
        assert "hidden" not in w._config_dict
        assert "_grid_saved" not in w._config_dict

    def test_grid_returns_self(self):
        w = _ConcreteWidget()
        assert w.grid() is w


# ── place ────────────────────────────────────────────────────────────


class TestPlace:
    def test_place_defaults(self):
        w = _ConcreteWidget()
        w.place()
        assert w._layout_mode == "place"
        assert w._layout_info["x"] == 0
        assert w._layout_info["y"] == 0

    def test_place_custom(self):
        w = _ConcreteWidget()
        w.place(x=10, y=20, width=100, height=50, anchor="center")
        assert w._layout_info["x"] == 10
        assert w._layout_info["y"] == 20
        assert w._layout_info["width"] == 100
        assert w._layout_info["height"] == 50

    def test_place_warns_mismatch(self):
        w = _ConcreteWidget()
        w.grid()
        with pytest.warns(UserWarning, match="place.*grid"):
            w.place()

    def test_place_returns_self(self):
        w = _ConcreteWidget()
        assert w.place() is w


# ── grid_remove / grid_forget ────────────────────────────────────────


class TestGridRemoveForget:
    def test_grid_remove(self):
        w = _ConcreteWidget()
        w.grid(row=1)
        w.grid_remove()
        assert w._config_dict["hidden"] is True
        assert w._config_dict["_grid_saved"]["row"] == 1

    def test_grid_forget(self):
        w = _ConcreteWidget()
        w.grid(row=1)
        w.grid_forget()
        assert w._config_dict["hidden"] is True
        assert "_grid_saved" not in w._config_dict


# ── config ───────────────────────────────────────────────────────────


class TestConfig:
    def test_config_state(self):
        w = _ConcreteWidget()
        w.config(state="disabled")
        assert w._config_dict["state"] == "disabled"

    def test_config_visible_true(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        with patch("iskg.app._HANDLERS", {}):
            w.config(visible=True)

    def test_config_visible_false(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        with patch("iskg.app._HANDLERS", {}):
            w.config(visible=False)

    def test_config_font(self):
        w = _ConcreteWidget()
        w.config(font="14px sans-serif")
        assert w._config_dict["font"] == "14px sans-serif"

    def test_config_textvariable(self):
        mock_var = Mock()
        mock_var._widgets = []
        w = _ConcreteWidget()
        w.config(textvariable=mock_var)
        assert w._textvariable is mock_var
        assert w in mock_var._widgets

    def test_config_variable(self):
        mock_var = Mock()
        mock_var._widgets = []
        w = _ConcreteWidget()
        w.config(variable=mock_var)
        assert w._variable is mock_var
        assert w in mock_var._widgets

    def test_config_tooltip(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.config(tooltip="hover me")
        assert w._config_dict["tooltip"] == "hover me"

    def test_config_unknown_key_warns(self):
        w = _ConcreteWidget()
        with pytest.warns(UserWarning, match="Unknown config key"):
            w.config(bogus_key=42)

    def test_config_known_key_validates(self):
        w = _ConcreteWidget()
        w.config(padding="10")  # px key, string with digit — OK
        assert w._config_dict["padding"] == "10"

    def test_config_returns_self(self):
        w = _ConcreteWidget()
        assert w.config(fg="red") is w

    def test_config_custom_prop(self):
        w = _ConcreteWidget()
        w.config(**{"--my-var": "blue"})
        assert w._config_dict["--my-var"] == "blue"
        # custom props should not warn

    def test_config_type_validation_raises(self):
        w = _ConcreteWidget()
        with pytest.raises(TypeError):
            w.config(text=42)

    def test_config_type_validation_skips_none(self):
        w = _ConcreteWidget()
        w.config(width=None)  # should not raise


# ── cget / _get_cfg ──────────────────────────────────────────────────


def test_cget():
    w = _ConcreteWidget(fg="red")
    assert w.cget("fg") == "red"


def test_cget_missing():
    w = _ConcreteWidget()
    assert w.cget("nonexistent") is None


def test_get_cfg_hyphen():
    w = _ConcreteWidget(font_size=16)
    assert w._get_cfg("font-size") == 16


def test_get_cfg_underscore_fallback():
    w = _ConcreteWidget(**{"font-size": 16})
    assert w._get_cfg("font-size") == 16


def test_get_cfg_default():
    w = _ConcreteWidget()
    assert w._get_cfg("missing", "default") == "default"


# ── _eval_js ─────────────────────────────────────────────────────────


class TestEvalJs:
    def test_eval_js_not_running(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = False
        w._eval_js("some_js()")  # should not call app._eval_js
        w._app._eval_js.assert_not_called()

    def test_eval_js_running(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w._eval_js("some_js()")
        w._app._eval_js.assert_called_once_with("some_js()")

    def test_eval_js_no_app(self):
        w = _ConcreteWidget()
        w._eval_js("some_js()")  # should not raise


# ── _set_font / _set_state ──────────────────────────────────────────


class TestSetFontState:
    def test_set_font_string(self):
        w = _ConcreteWidget()
        w._set_font("16px serif")
        assert w._config_dict["font"] == "16px serif"

    def test_set_font_list_full(self):
        w = _ConcreteWidget()
        w._set_font(["Arial", 12, "bold"])
        assert w._config_dict["font-family"] == "Arial"
        assert w._config_dict["font-size"] == 12
        assert w._config_dict["font-weight"] == "bold"

    def test_set_font_list_partial(self):
        w = _ConcreteWidget()
        w._set_font(["Courier"])
        assert w._config_dict["font-family"] == "Courier"
        assert "font-size" not in w._config_dict
        assert "font-weight" not in w._config_dict

    def test_set_font_tuple(self):
        w = _ConcreteWidget()
        w._set_font(("Monospace", 14))
        assert w._config_dict["font-family"] == "Monospace"
        assert w._config_dict["font-size"] == 14

    def test_set_state_normal(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w._set_state("normal")
        assert w._config_dict["disabled"] is False

    def test_set_state_disabled(self):
        w = _ConcreteWidget()
        w._set_state("disabled")
        assert w._config_dict["disabled"] is True

    def test_set_state_readonly(self):
        w = _ConcreteWidget()
        w._set_state("readonly")
        assert w._config_dict["disabled"] is False


# ── state / visible / width / height / cursor ──────────────────────


class TestStateProperties:
    def test_state_getter(self):
        w = _ConcreteWidget(state="disabled")
        assert w.state == "disabled"

    def test_state_getter_default(self):
        w = _ConcreteWidget()
        assert w.state == "normal"

    def test_state_setter(self):
        w = _ConcreteWidget()
        w.state = "readonly"
        assert w._config_dict["state"] == "readonly"

    def test_visible_getter_true(self):
        w = _ConcreteWidget()
        assert w.visible is True

    def test_visible_getter_false(self):
        w = _ConcreteWidget(hidden=True)
        assert w.visible is False

    def test_visible_setter_true(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.visible = True
        assert w._config_dict["hidden"] is False

    def test_visible_setter_false(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.visible = False
        assert w._config_dict["hidden"] is True

    def test_width_getter(self):
        w = _ConcreteWidget(width=200)
        assert w.width == 200

    def test_width_getter_none(self):
        w = _ConcreteWidget()
        assert w.width is None

    def test_width_setter(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.width = 300
        assert w._config_dict["width"] == 300

    def test_width_setter_none(self):
        w = _ConcreteWidget(width=200)
        w._app = Mock()
        w._app._running = True
        w.width = None
        assert "width" not in w._config_dict

    def test_height_getter(self):
        w = _ConcreteWidget(height=100)
        assert w.height == 100

    def test_height_setter(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.height = 150
        assert w._config_dict["height"] == 150

    def test_height_setter_none(self):
        w = _ConcreteWidget(height=100)
        w._app = Mock()
        w._app._running = True
        w.height = None
        assert "height" not in w._config_dict

    def test_cursor_getter(self):
        w = _ConcreteWidget(cursor="pointer")
        assert w.cursor == "pointer"

    def test_cursor_getter_default(self):
        w = _ConcreteWidget()
        assert w.cursor == "default"

    def test_cursor_setter(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.cursor = "grab"
        assert w._config_dict["cursor"] == "grab"


# ── focus / takefocus / focus_next / focus_prev ─────────────────────


class TestFocus:
    def test_focus(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.focus()

    def test_focus_set(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.focus_set()

    def test_takefocus_getter(self):
        w = _ConcreteWidget()
        assert w.takefocus is False  # default for Widget

    def test_takefocus_setter(self):
        w = _ConcreteWidget()
        w.takefocus = True
        assert w._config_dict["takefocus"] is True

    def test_default_takefocus(self):
        w = _ConcreteWidget()
        assert w._default_takefocus() is False

    def test_tabindex_attr_true(self):
        assert Widget._tabindex_attr(True) == ' tabindex="0"'

    def test_tabindex_attr_false(self):
        assert Widget._tabindex_attr(False) == ""

    def test_collect_focusable(self):
        parent = _ConcreteWidget()
        parent.takefocus = True
        child = _ConcreteWidget(parent=parent)
        child.takefocus = True
        result = parent._collect_focusable()
        assert parent in result
        assert child in result

    def test_collect_focusable_skips_destroyed(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        child._destroyed = True
        result = parent._collect_focusable()
        assert child not in result

    def test_focus_next(self):
        p = _ConcreteWidget()
        p.takefocus = True
        c1 = _ConcreteWidget(parent=p)
        c1.takefocus = True
        c2 = _ConcreteWidget(parent=p)
        c2.takefocus = True
        c1.focus_next()

    def test_focus_next_empty_chain(self):
        w = _ConcreteWidget()
        w.focus_next()  # should not raise

    def test_focus_next_value_error(self):
        w = _ConcreteWidget()
        w.takefocus = False
        c = _ConcreteWidget(parent=w)
        c.takefocus = True
        w.focus_next()  # self not in chain → picks chain[0]

    def test_focus_prev(self):
        p = _ConcreteWidget()
        p.takefocus = True
        c1 = _ConcreteWidget(parent=p)
        c1.takefocus = True
        c1.focus_prev()

    def test_focus_prev_empty_chain(self):
        w = _ConcreteWidget()
        w.focus_prev()  # should not raise

    def test_focus_prev_value_error(self):
        w = _ConcreteWidget()
        w.takefocus = False
        c = _ConcreteWidget(parent=w)
        c.takefocus = True
        w.focus_prev()  # self not in chain → picks chain[-1]

    def test_collect_focusable_into_destroyed(self):
        w = _ConcreteWidget()
        w._destroyed = True
        result = []
        w._collect_focusable_into(result)
        assert result == []


# ── hide / show / update ────────────────────────────────────────────


class TestHideShow:
    def test_hide(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.hide()
        assert w.visible is False

    def test_show(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.show()
        assert w.visible is True

    def test_update(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.update()  # should not raise


# ── after / after_cancel ────────────────────────────────────────────


class TestAfter:
    def test_after_creates_timer(self):
        w = _ConcreteWidget()
        timer = w.after(100, lambda: None)
        assert timer.running is True
        assert timer._id.startswith("t")

    def test_after_cancel_by_obj(self):
        w = _ConcreteWidget()
        timer = w.after(10000, lambda: None)  # long enough
        timer.cancel()
        assert timer.running is False

    def test_after_cancel_by_id(self):
        w = _ConcreteWidget()
        timer = w.after(10000, lambda: None)
        w.after_cancel(timer._id)
        assert timer.running is False

    def test_after_cancel_unknown_id(self):
        w = _ConcreteWidget()
        w.after_cancel("nonexistent")  # should not raise

    def test_after_zero_ms(self):
        w = _ConcreteWidget()
        called = []
        t = w.after(0, lambda: called.append(1))
        assert t.running is True
        t.cancel()

    def test_after_negative_ms(self):
        w = _ConcreteWidget()
        t = w.after(-100, lambda: None)  # Timer accepts negative→fires immediately
        assert t.running is True
        t.cancel()

    def test_after_cancel_by_object(self):
        w = _ConcreteWidget()
        t = w.after(5000, lambda: None)
        t.cancel()
        assert t.running is False


# ── _parse_key_event ────────────────────────────────────────────────


class TestParseKeyEvent:
    def test_parse_keypress_a(self):
        result = Widget._parse_key_event("<KeyPress-a>")
        assert result["event_type"] == "keypress"
        assert result["key"] == "a"

    def test_parse_keyrelease_return(self):
        result = Widget._parse_key_event("<KeyRelease-Return>")
        assert result["event_type"] == "keyrelease"
        assert result["key"] == "Return"

    def test_parse_control_c(self):
        result = Widget._parse_key_event("<Control-c>")
        assert result["ctrl"] is True
        assert result["key"] == "c"

    def test_parse_alt_shift_x(self):
        result = Widget._parse_key_event("<Alt-Shift-x>")
        assert result["alt"] is True
        assert result["shift"] is True
        assert result["key"] == "x"

    def test_parse_plain_key(self):
        result = Widget._parse_key_event("<Key>")
        assert result["event_type"] == "keypress"
        assert result["key"] is None

    def test_parse_non_event_returns_none(self):
        assert Widget._parse_key_event("click") is None

    def test_parse_virtual_event_returns_none(self):
        assert Widget._parse_key_event("<<Custom>>") is None


# ── bind / unbind / key bindings ────────────────────────────────────


class TestBindUnbind:
    def test_bind_simple_event(self):
        w = _ConcreteWidget()
        cb = Mock()
        w.bind("click", cb)
        assert w._bindings.get("click") is cb

    def test_bind_key_event(self):
        w = _ConcreteWidget()
        cb = Mock()
        w.bind("<KeyPress-a>", cb)
        assert len(w._key_bindings) == 1
        assert w._key_bindings[0]["key"] == "a"

    def test_install_key_binding_with_running_app(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        parsed = {"event_type": "keypress", "key": "x", "ctrl": True, "alt": False, "shift": False}
        with patch("iskg.app._HANDLERS", {}):
            w._install_key_binding(parsed, Mock())

    def test_render_key_binding_js_with_mods(self):
        parsed = {"ctrl": True, "alt": True, "shift": True, "key": "c", "event_type": "keypress"}
        w = _ConcreteWidget()
        js = w._render_key_binding_js(parsed)
        assert "ctrl" in js
        assert "alt" in js
        assert "shift" in js
        assert "c" in js

    def test_unbind_simple_event(self):
        w = _ConcreteWidget()
        w.bind("click", Mock())
        w.unbind("click")
        assert "click" not in w._bindings

    def test_unbind_key_event(self):
        w = _ConcreteWidget()
        w.bind("<Control-c>", Mock())
        w.unbind("<Control-c>")
        assert len(w._key_bindings) == 0

    def test_unbind_key_event_with_running_app(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        with patch("iskg.app._HANDLERS", {}):
            w.bind("<KeyPress-a>", Mock())
            w.unbind("<KeyPress-a>")

    def test_unbind_nonexistent(self):
        w = _ConcreteWidget()
        w.unbind("click")  # should not raise

    def test_render_key_bindings_js(self):
        w = _ConcreteWidget()
        w.bind("<KeyPress-a>", Mock())
        js = w._render_key_bindings_js()
        assert "iskg_bind_key" in js


# ── event_generate / _handle_bridge_event ────────────────────────────


class TestEventGenerate:
    def test_event_generate_bubbles(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        parent._bindings["custom"] = Mock(return_value=None)
        assert child.event_generate("custom") is False
        parent._bindings["custom"].assert_called_once()

    def test_event_generate_break_stops(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        parent._bindings["custom"] = Mock(return_value="break")
        assert child.event_generate("custom") is True

    def test_handle_bridge_change_sets_textvariable(self):
        w = _ConcreteWidget()
        mock_var = Mock()
        mock_var._widgets = [w]
        w._textvariable = mock_var
        w._handle_bridge_event("change", "new value")
        mock_var.set.assert_called_once_with("new value", _from_widget=w)

    def test_handle_bridge_change_sets_variable(self):
        w = _ConcreteWidget()
        mock_var = Mock()
        mock_var._widgets = [w]
        w._variable = mock_var
        w._handle_bridge_event("change", 42)
        mock_var.set.assert_called_once_with(42, _from_widget=w)

    def test_handle_bridge_event_callback_break(self):
        w = _ConcreteWidget()
        w._bindings["click"] = Mock(return_value="break")
        cmd = Mock()
        w._config_dict["command"] = cmd
        result = w._handle_bridge_event("click", None)
        assert result == "break"
        cmd.assert_not_called()

    def test_handle_bridge_event_command_on_click(self):
        w = _ConcreteWidget()
        cmd = Mock()
        w._config_dict["command"] = cmd
        w._handle_bridge_event("click", None)
        cmd.assert_called_once()


# ── destroy ──────────────────────────────────────────────────────────


class TestDestroy:
    def test_destroy_sets_flag(self):
        w = _ConcreteWidget()
        w.destroy()
        assert w._destroyed is True

    def test_destroy_removes_from_parent(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        child.destroy()
        assert child not in parent._children

    def test_destroy_calls_app_widget_destroyed(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w.destroy()
        w._app._widget_destroyed.assert_called_once_with(w._id)

    def test_destroy_destroys_children(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        parent.destroy()
        assert child._destroyed is True


# ── _render / _render_style / _render_style_css ─────────────────────


class TestRenderStyle:
    def test_render_hidden(self):
        w = _ConcreteWidget(hidden=True)
        style = w._render_style()
        assert "display:none" in style

    def test_render_pack_left_no_expand(self):
        w = _WidgetWithRender()
        w.pack(side="left")
        html = w._render()
        assert "flex-shrink:0" in html

    def test_render_pack_left_expand(self):
        w = _ConcreteWidget()
        w.pack(side="left", expand=True)
        style = w._render_style()
        assert "flex:1" in style

    def test_render_pack_fill_y(self):
        w = _ConcreteWidget()
        w.pack(side="left", fill="y")
        style = w._render_style()
        assert "align-self:stretch" in style

    def test_render_pack_fill_x_expand(self):
        w = _ConcreteWidget()
        w.pack(side="left", fill="x", expand=True)
        style = w._render_style()
        assert "align-self:stretch" not in style  # fill x on side left
        # fill x with expand on side=left should add width:100%
        assert "width:100%" in style

    def test_render_pack_right_no_expand(self):
        w = _ConcreteWidget()
        w.pack(side="right")
        style = w._render_style()
        assert "margin-left:auto" in style

    def test_render_pack_top_expand(self):
        w = _ConcreteWidget()
        w.pack(side="top", expand=True)
        style = w._render_style()
        assert "flex:1" in style

    def test_render_pack_fill_x_top(self):
        w = _ConcreteWidget()
        w.pack(side="top", fill="x")
        style = w._render_style()
        assert "align-self:stretch" in style

    def test_render_pack_fill_y_top_no_expand(self):
        w = _ConcreteWidget()
        w.pack(side="top", fill="y")
        style = w._render_style()
        assert "height:100%" in style

    def test_render_pack_right_bottom(self):
        w = _ConcreteWidget()
        w.pack(side="bottom")
        style = w._render_style()
        assert "margin-top:auto" in style

    def test_render_pack_padx(self):
        w = _ConcreteWidget()
        w.pack(padx=10)
        style = w._render_style()
        assert "padding-left:10px" in style
        assert "padding-right:10px" in style

    def test_render_pack_pady(self):
        w = _ConcreteWidget()
        w.pack(pady=15)
        style = w._render_style()
        assert "padding-top:15px" in style

    def test_render_grid_basic(self):
        w = _ConcreteWidget()
        w.grid(row=0, column=1, rowspan=2, columnspan=3)
        style = w._render_style()
        assert "grid-row:1/span 2" in style
        assert "grid-column:2/span 3" in style

    def test_render_grid_padx(self):
        w = _ConcreteWidget()
        w.grid(padx=8)
        style = w._render_style()
        assert "padding-left:8px" in style

    def test_render_grid_pady(self):
        w = _ConcreteWidget()
        w.grid(pady=12)
        style = w._render_style()
        assert "padding-top:12px" in style

    def test_render_grid_sticky_we(self):
        w = _ConcreteWidget()
        w.grid(sticky="we")
        style = w._render_style()
        assert "justify-self:stretch" in style

    def test_render_grid_sticky_w(self):
        w = _ConcreteWidget()
        w.grid(sticky="w")
        style = w._render_style()
        assert "justify-self:start" in style

    def test_render_grid_sticky_e(self):
        w = _ConcreteWidget()
        w.grid(sticky="e")
        style = w._render_style()
        assert "justify-self:end" in style

    def test_render_grid_sticky_c(self):
        w = _ConcreteWidget()
        w.grid(sticky="c")
        style = w._render_style()
        assert "justify-self:center" in style

    def test_render_grid_sticky_ns(self):
        w = _ConcreteWidget()
        w.grid(sticky="ns")
        style = w._render_style()
        assert "align-self:stretch" in style

    def test_render_grid_sticky_n(self):
        w = _ConcreteWidget()
        w.grid(sticky="n")
        style = w._render_style()
        assert "align-self:start" in style

    def test_render_grid_sticky_s(self):
        w = _ConcreteWidget()
        w.grid(sticky="s")
        style = w._render_style()
        assert "align-self:end" in style

    def test_render_grid_sticky_nsew(self):
        w = _ConcreteWidget()
        w.grid(sticky="nsew")
        style = w._render_style()
        assert "justify-self:stretch" in style
        assert "align-self:stretch" in style

    def test_render_grid_sticky_ns_c(self):
        w = _ConcreteWidget()
        w.grid(sticky="nsc")
        style = w._render_style()
        assert "align-self:stretch" in style
        assert "justify-self:center" in style

    def test_render_place(self):
        w = _ConcreteWidget()
        w.place(x=5, y=10, width=200, height=100)
        style = w._render_style()
        assert "position:absolute" in style
        assert "left:5px" in style
        assert "top:10px" in style
        assert "width:200px" in style
        assert "height:100px" in style

    def test_render_place_no_size(self):
        w = _ConcreteWidget()
        w.place(x=5, y=10)
        style = w._render_style()
        assert "position:absolute" in style
        assert "width:" not in style
        assert "height:" not in style

    def test_render_style_css(self):
        w = _ConcreteWidget(fg="red", padding=10)
        css = w._render_style_css()
        assert "color:red" in css
        assert "padding:10px" in css

    def test_render_style_css_custom_prop(self):
        w = _ConcreteWidget(**{"--my-prop": "20px"})
        css = w._render_style_css()
        assert "--my-prop:20px" in css

    def test_render_no_layout(self):
        w = _WidgetWithRender()
        html = w._render()
        assert "span" in html
        assert "text" in html

    def test_render_base_no_layout(self):
        w = _ConcreteWidget()
        assert w._render() == ""

    def test_render_grid_layout(self):
        w = _WidgetWithRender()
        w.grid()
        html = w._render()
        assert "div" in html
        assert "grid-row" in html


# ── _render_children / _render_children_js / _collect_widgets ─────


class TestRenderChildren:
    def test_render_children_empty(self):
        w = _ConcreteWidget()
        assert w._render_children() == ""

    def test_render_children_skips_destroyed(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        child._destroyed = True
        result = parent._render_children()
        assert result == ""

    def test_render_children_with_widgets(self):
        parent = _WidgetWithRender()
        child = _WidgetWithRender(parent=parent)
        child.grid()
        result = parent._render_children()
        assert child._id in result

    def test_render_children_js_empty(self):
        w = _ConcreteWidget()
        assert w._render_children_js() == ""

    def test_render_children_js_skips_destroyed(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        child._destroyed = True
        js = parent._render_children_js()
        assert js == ""

    def test_render_children_js_with_bindings(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        child.bind("<KeyPress-a>", Mock())
        js = parent._render_children_js()
        assert "iskg_bind_key" in js

    def test_collect_widgets(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        result = parent._collect_widgets()
        assert (0, parent) in result
        assert (1, child) in result

    def test_collect_widgets_skips_destroyed(self):
        parent = _ConcreteWidget()
        child = _ConcreteWidget(parent=parent)
        child._destroyed = True
        result = parent._collect_widgets()
        assert child not in [w for _, w in result]


# ── _sync / render update ───────────────────────────────────────────


class TestSync:
    def test_sync_no_app(self):
        w = _ConcreteWidget()
        w._sync()  # should not raise

    def test_sync_not_running(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = False
        w._sync()

    def test_sync_destroyed(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w.destroy()
        w._sync()

    def test_sync_calls_eval_with_style(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w._config_dict["fg"] = "red"
        w._sync()
        w._app._eval_js.assert_called_once()

    def test_sync_calls_eval_with_update_js(self):
        w = _WidgetWithUpdateJs()
        w._app = Mock()
        w._app._running = True
        w._sync()
        w._app._eval_js.assert_called_once()

    def test_sync_calls_eval_with_attr_js(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w._config_dict["disabled"] = True
        w._sync()
        w._app._eval_js.assert_called_once()

    def test_sync_skips_duplicate_js(self):
        w = _ConcreteWidget()
        w._app = Mock()
        w._app._running = True
        w._config_dict["fg"] = "red"
        w._sync()
        first_call = w._app._eval_js.call_count
        w._sync()  # same JS → skipped
        assert w._app._eval_js.call_count == first_call

    def test_render_update_js_default(self):
        w = _ConcreteWidget()
        assert w._render_update_js() == ""

    def test_render_attr_update_js_disabled(self):
        w = _ConcreteWidget()
        w._config_dict["disabled"] = True
        js = w._render_attr_update_js()
        assert "iskg_set_enabled" in js
        assert "false" in js

    def test_render_attr_update_js_enabled(self):
        w = _ConcreteWidget()
        w._config_dict["disabled"] = False
        js = w._render_attr_update_js()
        assert "iskg_set_enabled" in js
        assert "true" in js

    def test_render_attr_update_js_none(self):
        w = _ConcreteWidget()
        assert w._render_attr_update_js() == ""

    def test_render_attrs_disabled(self):
        w = _ConcreteWidget()
        w._config_dict["disabled"] = True
        attrs = w._render_attrs()
        assert " disabled" in attrs

    def test_render_style_update_js_with_css(self):
        w = _ConcreteWidget(fg="red")
        js = w._render_style_update_js()
        assert "iskg_set_style" in js

    def test_render_style_update_js_empty(self):
        w = _ConcreteWidget()
        assert w._render_style_update_js() == ""

    def test_render_style_update_js_caches(self):
        w = _ConcreteWidget(fg="red")
        first = w._render_style_update_js()
        assert first != ""
        second = w._render_style_update_js()  # same CSS → cached
        assert second == ""

    def test_render_style_update_js_after_change(self):
        w = _ConcreteWidget(fg="red")
        w._render_style_update_js()
        w._config_dict["fg"] = "blue"
        third = w._render_style_update_js()
        assert "blue" in third


# ── _css_value ───────────────────────────────────────────────────────


class TestCssValue:
    def test_int_px(self):
        assert Widget._css_value(10, True) == "10px"

    def test_float_px(self):
        assert Widget._css_value(1.5, True) == "1.5px"

    def test_str_px_with_digit(self):
        assert Widget._css_value("10px", True) == "10px"

    def test_str_multi_px(self):
        result = Widget._css_value("5 10", True)
        assert "5px" in result
        assert "10px" in result

    def test_str_non_px(self):
        assert Widget._css_value("red", False) == "red"

    def test_int_non_px(self):
        assert Widget._css_value(0, False) == "0"


# ── _var_updated ─────────────────────────────────────────────────────


def test_var_updated_noop():
    w = _ConcreteWidget()
    w._var_updated(None)  # no-op, should not raise
