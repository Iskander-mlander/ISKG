import pytest
from iskg import Widget


def test_widget_defaults():
    w = Widget()
    assert w._layout_mode is None
    assert w._destroyed is False
    assert w.widget_id.startswith("iw")
    assert w.parent is None
    assert w.app is None


def test_widget_pack_layout():
    w = Widget()
    result = w.pack(side="top", fill="both", expand=True, padx=4, pady=4)
    assert result is w
    assert w._layout_mode == "pack"
    assert w._layout_info["side"] == "top"
    assert w._layout_info["expand"] is True


def test_widget_grid_layout():
    w = Widget()
    w.grid(row=1, column=2, rowspan=2, columnspan=3, sticky="we", padx=2, pady=2)
    assert w._layout_mode == "grid"
    assert w._layout_info["row"] == 1
    assert w._layout_info["column"] == 2
    assert w._layout_info["sticky"] == "we"


def test_widget_place_layout():
    w = Widget()
    w.place(x=10, y=20, width=100, height=50)
    assert w._layout_mode == "place"
    assert w._layout_info["x"] == 10
    assert w._layout_info["y"] == 20


def test_widget_config_and_cget():
    w = Widget()
    w.config(fg="red", font_size=14, bg="#0a0e17")
    assert w.cget("fg") == "red"
    assert w.cget("font_size") is not None
    assert w.cget("bg") == "#0a0e17"


def test_widget_bind_unbind():
    w = Widget()
    called = []

    def handler(val):
        called.append(val)

    w.bind("change", handler)
    assert "change" in w._bindings
    w.unbind("change")
    assert "change" not in w._bindings


def test_widget_add_remove_child():
    parent = Widget()
    child = Widget()
    parent.add(child)
    assert child in parent._children
    assert child.parent is parent
    parent.remove(child)
    assert child not in parent._children
    assert child.parent is None


def test_widget_destroy():
    parent = Widget()
    child = Widget(parent=parent)
    child.destroy()
    assert child._destroyed is True
    assert child not in parent._children
    assert child.parent is None


def test_widget_render_default():
    w = Widget()
    assert w._render() == ""
    assert w._render_js() == ""
    assert w._render_update_js() == ""
