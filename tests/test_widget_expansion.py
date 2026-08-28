"""Tests for the widget expansion in 0.4.6+: new widgets (ColorPicker,
FileBrowser, Modal, TabBar, RangeSlider), property consistency
(``enabled``, ``readonly``, ``from_/to``, ``selected_index``), and
bug fixes (``ImageBox.fit`` validation, ``Clock.stop()``,
``Notebook`` runtime API, ``PanedWindow.sash_pos`` as a property).
"""

from iskg import (
    Application,
    Button,
    CheckBox,
    Clock,
    ColorPicker,
    DataGrid,
    DatePicker,
    Entry,
    FileBrowser,
    Frame,
    ImageBox,
    Label,
    ListBox,
    Modal,
    Notebook,
    PanedWindow,
    RadioButton,
    RangeSlider,
    Scale,
    Slider,
    SpinBox,
    StatusBar,
    TabBar,
    Text,
    ToggleSwitch,
    TreeView,
)

# ─── First-positional text (consistency) ───────────────────────────────


def test_positional_text_checkbox():
    cb = CheckBox("Mi check")
    assert cb._config_dict.get("text") == "Mi check"


def test_positional_text_radiobutton():
    rb = RadioButton("Opción A", group="g1")
    assert rb._config_dict.get("text") == "Opción A"
    assert rb.group == "g1"


def test_positional_text_toggle():
    ts = ToggleSwitch("on/off")
    assert ts._config_dict.get("text") == "on/off"


def test_positional_text_text():
    t = Text("multilinea\nsiguiente")
    assert t.text == "multilinea\nsiguiente"


def test_positional_text_richtext():
    rt = Text("<b>html</b>")
    assert rt.text == "<b>html</b>"


def test_positional_text_iconlabel():
    il = Label("texto", font="bold 16px")
    assert il.text == "texto"


# ─── enabled property ───────────────────────────────────────────────────


def test_button_enabled():
    b = Button("X")
    assert b.enabled is True
    b.enabled = False
    assert b.enabled is False
    assert b._config_dict.get("disabled") is True


def test_checkbox_enabled():
    cb = CheckBox("X")
    cb.enabled = False
    assert cb._config_dict.get("disabled") is True


def test_radiobutton_enabled():
    rb = RadioButton("X")
    rb.enabled = False
    assert rb._config_dict.get("disabled") is True


def test_toggle_enabled():
    t = ToggleSwitch("X")
    t.enabled = False
    assert t._config_dict.get("disabled") is True


def test_slider_enabled():
    s = Slider()
    s.enabled = False
    assert s._config_dict.get("disabled") is True


def test_spinbox_enabled():
    s = SpinBox()
    s.enabled = False
    assert s._config_dict.get("disabled") is True


# ─── readonly on Entry/Text ────────────────────────────────────────────


def test_entry_readonly():
    e = Entry(text="hola")
    assert e.readonly is False
    e.readonly = True
    assert e.readonly is True


def test_text_readonly():
    t = Text("contenido")
    assert t.readonly is False
    t.readonly = True
    assert t.readonly is True


# ─── Slider/SpinBox reactive range ─────────────────────────────────────


def test_slider_from_to_reactive():
    s = Slider(value=50, from_=0, to=100)
    assert s.from_ == 0 and s.to == 100
    s.from_ = -10
    s.to = 50
    assert s.from_ == -10 and s.to == 50


def test_slider_step_reactive():
    s = Slider()
    s.step = 0.5
    assert s.step == 0.5
    s.step = None
    assert s.step is None


def test_slider_orient_reactive():
    s = Slider()
    s.orient = "vertical"
    assert s.orient == "vertical"


def test_slider_show_value_reactive():
    s = Slider()
    s.show_value = False
    assert s.show_value is False


def test_spinbox_min_max_reactive():
    sp = SpinBox(value=5)
    sp.min_value = 1
    sp.max_value = 10
    assert sp.from_ == 1 and sp.to == 10


def test_scale_updates_labels():
    sc = Scale(value=0.5, from_=0, to=1)
    sc.from_ = 0
    sc.to = 100
    assert sc.from_ == 0 and sc.to == 100


# ─── ListBox selection ─────────────────────────────────────────────────


def test_listbox_select_insert_preserves_selection():
    lb = ListBox(items=["a", "b", "c"])
    lb.selected_index = 1
    lb.insert(0, "z")  # inserts before selected
    assert lb.selected_index == 2


def test_listbox_delete_updates_selection():
    lb = ListBox(items=["a", "b", "c"])
    lb.selected_index = 1
    lb.delete(1)
    assert lb.selected_index == -1


def test_listbox_clear_resets_selection():
    lb = ListBox(items=["a", "b"])
    lb.selected_index = 0
    lb.clear()
    assert lb.selected_index == -1


def test_listbox_command_passes_index_and_text():
    lb = ListBox(items=["foo", "bar"])
    calls = []

    def cb(idx_text: str) -> None:
        calls.append(idx_text)

    lb.bind("change", cb)
    # Simulate the JS bridge event with the "idx:text" format the new
    # _render_js emits.
    lb._handle_bridge_event("change", "0:foo")
    assert calls == ["0:foo"]


# ─── DataGrid runtime API ──────────────────────────────────────────────


def test_datagrid_columns_reactive():
    dg = DataGrid(columns=["a", "b"], rows=[["1", "2"]])
    dg.columns = ["x", "y", "z"]
    assert dg._config_dict["columns"] == ["x", "y", "z"]


def test_datagrid_append_row_widens_short_row():
    dg = DataGrid(columns=["a", "b", "c"], rows=[])
    dg.append_row(["1"])
    assert dg.rows == [["1", "", ""]]


def test_datagrid_remove_row_updates_selection():
    dg = DataGrid(columns=["a"], rows=[["1"], ["2"], ["3"]])
    dg.selected_row = 1
    dg.remove_row(0)
    assert dg.selected_row == 0  # shifted up


# ─── TreeView runtime API ─────────────────────────────────────────────


def test_treeview_add_root():
    tv = TreeView()
    tv.add("root_item")
    assert tv.items[0]["text"] == "root_item"


def test_treeview_add_nested():
    tv = TreeView(items=[{"text": "parent", "children": []}])
    tv.add({"text": "child"}, parent_path="parent")
    assert tv.items[0]["children"][0]["text"] == "child"


def test_treeview_remove():
    tv = TreeView(items=[{"text": "a"}, {"text": "b"}])
    assert tv.remove_node("a") is True
    assert len(tv.items) == 1


def test_treeview_clear():
    tv = TreeView(items=[{"text": "a"}])
    tv.clear()
    assert tv.items == []


# ─── Notebook API ──────────────────────────────────────────────────────


def test_notebook_remove_tab():
    nb = Notebook()
    a = Label("a")
    b = Label("b")
    nb.add_tab("A", a)
    nb.add_tab("B", b)
    assert nb.tab_count == 2
    assert nb.remove_tab(0) is True
    assert nb.tab_count == 1


def test_notebook_set_active():
    nb = Notebook()
    nb.add_tab("A", Label("a"))
    nb.add_tab("B", Label("b"))
    nb.current_tab = 1
    assert nb.current_tab == 1


# ─── PanedWindow.sash_pos as property ──────────────────────────────────


def test_panedwindow_sash_pos_property():
    pw = PanedWindow()
    pw.sash_pos = 0.75
    assert pw.sash_pos == 0.75
    pw.sash_pos = 1.5
    assert pw.sash_pos == 1.0


# ─── Frame.text reactive ───────────────────────────────────────────────


def test_frame_text_reactive():
    f = Frame(text="Original")
    f.text = "Nuevo"
    assert f._config_dict["text"] == "Nuevo"


# ─── ImageBox.fit validation ───────────────────────────────────────────


def test_imagebox_fit_validates_known_values():
    ImageBox(fit="cover")  # OK
    ImageBox(fit="fill")  # OK


def test_imagebox_fit_rejects_invalid():
    import pytest

    with pytest.raises(ValueError):
        ImageBox(fit="bogus")


def test_imagebox_fit_setter_validates():
    img = ImageBox()
    import pytest

    with pytest.raises(ValueError):
        img.fit = "bogus"


# ─── Clock.stop/start ─────────────────────────────────────────────────


def test_clock_has_stop_and_start():
    cl = Clock()
    assert hasattr(cl, "stop")
    assert hasattr(cl, "start")


# ─── DatePicker.format_ ───────────────────────────────────────────────


def test_datepicker_format_property():
    from datetime import date

    dp = DatePicker(date=date(2026, 1, 1), format_="%d/%m/%Y")
    assert dp.date_format == "%d/%m/%Y"
    dp.date_format = "%Y/%m/%d"
    assert dp.date_format == "%Y/%m/%d"


def test_datepicker_value_setter():
    from datetime import date

    dp = DatePicker()
    dp.value = date(2025, 12, 31)
    assert dp.value == date(2025, 12, 31)


# ─── StatusBar.text no side effect ─────────────────────────────────────


def test_statusbar_text_no_mutation_of_input_list():
    sections = [{"text": "old"}]
    sb = StatusBar(sections=sections)
    sb.text = "new"
    # The internal list has been replaced, not mutated in place
    assert sections[0]["text"] == "old"
    assert sb._config_dict["sections"][0]["text"] == "new"


# ─── New widgets render and export ────────────────────────────────────


def test_colorpicker_renders():
    cp = ColorPicker(color="#ff0000")
    app = Application("t")
    app.add(Frame(parent=None).grid_columnconfigure(0, weight=1) or Frame())
    app.add(cp)
    loop = app.test_loop()
    assert cp.color == "#ff0000"
    assert "iskg-colorpicker" in loop.html
    assert "ff0000" in loop.html


def test_colorpicker_setter_validates_format():
    cp = ColorPicker()
    cp.color = "00ff00"
    assert cp.color == "#00ff00"


def test_fb_renders(tmp_path):
    fb = FileBrowser(root=str(tmp_path), width=200, height=100)
    (tmp_path / "a.txt").write_text("hi")
    app = Application("t")
    app.add(fb)
    loop = app.test_loop()
    assert "iskg-fb" in loop.html
    assert str(tmp_path) in loop.html


def test_modal_show_hide():
    m = Modal(title="hi", width=200, height=100)
    assert m.visible is False
    m.show()
    assert m.visible is True
    m.hide()
    assert m.visible is False


def test_tabbar_runtime_api():
    tb = TabBar()
    tb.add_tab("A")
    tb.add_tab("B")
    tb.add_tab("C")
    assert tb.tab_count == 3
    tb.current_tab = 2
    assert tb.current_tab == 2
    assert tb.remove_tab(1) is True
    assert tb.tab_count == 2


def test_rangeslider_low_high_clamping():
    rs = RangeSlider(low=20, high=80, from_=0, to=100)
    rs.low = 90  # > high, should clamp
    assert rs.low == 80
    rs.high = 10  # < low, should clamp
    assert rs.high == 80


def test_rangeslider_range_property():
    rs = RangeSlider(low=20, high=80)
    rs.range = (10, 50)
    assert rs.low == 10 and rs.high == 50
    # Reverse order is normalised
    rs.range = (90, 20)
    assert rs.low == 20 and rs.high == 90
