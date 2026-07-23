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


def test_get_cfg_hyphen_vs_underscore():
    w = Widget()
    w._config_dict["foo-bar"] = "hyphen"
    w._config_dict["baz_qux"] = "underscore"

    # hyphen key found directly
    assert w._get_cfg("foo-bar") == "hyphen"
    # underscore key found via fallback
    assert w._get_cfg("baz-qux") == "underscore"
    # missing key returns default
    assert w._get_cfg("missing", 42) == 42


def test_render_attr_update_js():
    w = Widget()
    # no disabled set → no JS
    assert w._render_attr_update_js() == ""

    # disabled=True produces JS
    w._config_dict["disabled"] = True
    js = w._render_attr_update_js()
    assert "iskg_set_enabled" in js
    assert "false" in js

    w._config_dict["disabled"] = False
    js = w._render_attr_update_js()
    assert "iskg_set_enabled" in js
    assert "true" in js


def test_layout_mix_warning():
    w = Widget()
    w.pack(side="top")
    with pytest.warns(UserWarning, match="grid.*pack"):
        w.grid(row=0, column=0)
    with pytest.warns(UserWarning, match="place.*grid"):
        w.place(x=0, y=0)


def test_unknown_config_key_warning():
    w = Widget()
    with pytest.warns(UserWarning, match="Unknown config key"):
        w.config(**{"unknown-prop": "val"})

    # known keys should NOT warn
    import warnings as _warnings

    with _warnings.catch_warnings(record=True) as record:
        _warnings.simplefilter("always")
        w2 = Widget()
        w2.config(fg="red")
        w2.config(font_size=14)
        w2.config(margin=5)
    unknown = [r for r in record if "Unknown config key" in str(r.message)]
    assert len(unknown) == 0
