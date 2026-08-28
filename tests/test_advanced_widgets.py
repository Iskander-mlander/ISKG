"""Tests for the 0.4.7 expansion: validation, i18n, pickers, calendar,
charts, toolbar/MDI, undo/redo, debug tools.
"""

import datetime as _dt

import iskg
from iskg import (
    Avatar,
    Badge,
    BarChart,
    Calendar,
    Carousel,
    CommandPalette,
    CustomValidator,
    DateTimePicker,
    EmailValidator,
    Entry,
    FileBrowser,
    FontPicker,
    Form,
    Frame,
    GraphicsView,
    Heatmap,
    ImagePicker,
    LengthValidator,
    Logger,
    MarkdownViewer,
    MdiArea,
    MdiSubWindow,
    Modal,
    NumberValidator,
    PatternValidator,
    PieChart,
    ProgressCircle,
    PropertyGrid,
    RangeValidator,
    RequiredValidator,
    ScatterPlot,
    SearchCtrl,
    Spinner,
    TimePicker,
    ToolBar,
    UndoCommand,
    UndoStack,
    URLValidator,
    qDebug,
    render_markdown,
    set_language,
    tr,
)

# ─── Validation ────────────────────────────────────────────────────────


def test_required_validator_rejects_empty():
    e = Entry()
    v = RequiredValidator("required")
    v.attach(e)
    res = v.check()
    assert not res.is_valid
    assert "required" in res.message


def test_required_validator_accepts_text():
    e = Entry(text="hello")
    v = RequiredValidator().attach(e)
    assert v.check().is_valid


def test_email_validator():
    v = EmailValidator().attach(Entry(text="foo@bar.com"))
    assert v.check().is_valid
    v2 = EmailValidator().attach(Entry(text="not-an-email"))
    assert not v2.check().is_valid


def test_url_validator():
    v = URLValidator().attach(Entry(text="https://example.com/x"))
    assert v.check().is_valid
    v2 = URLValidator().attach(Entry(text="ftp://x"))
    assert not v2.check().is_valid


def test_number_validator():
    v = NumberValidator().attach(Entry(text="123.45"))
    assert v.check().is_valid
    v2 = NumberValidator().attach(Entry(text="abc"))
    assert not v2.check().is_valid


def test_length_validator():
    v = LengthValidator(min_len=3, max_len=10).attach(Entry(text="hello"))
    assert v.check().is_valid
    v2 = LengthValidator(max_len=2).attach(Entry(text="hello"))
    assert not v2.check().is_valid


def test_range_validator():
    v = RangeValidator(0, 100).attach(Entry(text="50"))
    assert v.check().is_valid
    v2 = RangeValidator(0, 100).attach(Entry(text="150"))
    assert not v2.check().is_valid


def test_pattern_validator():
    v = PatternValidator(r"^\d{3}-\d{4}$").attach(Entry(text="123-4567"))
    assert v.check().is_valid
    v2 = PatternValidator(r"^\d{3}-\d{4}$").attach(Entry(text="123-45678"))
    assert not v2.check().is_valid


def test_custom_validator():
    v = CustomValidator(lambda x: int(x) > 0, "must be positive").attach(Entry(text="5"))
    assert v.check().is_valid
    v2 = CustomValidator(lambda x: int(x) > 0).attach(Entry(text="-1"))
    assert not v2.check().is_valid


def test_form_collect():
    f = Form()
    e1 = Entry(text="alice")
    e2 = Entry(text="a@b.com")
    f.add_field(e1, RequiredValidator())
    f.add_field(e2, [RequiredValidator(), EmailValidator()])
    assert f.is_valid
    data = f.collect()
    assert "alice" in data.values()
    assert "a@b.com" in data.values()


def test_form_invalid_collects_errors():
    f = Form()
    f.add_field(Entry(text=""), RequiredValidator())
    assert not f.is_valid
    assert f.errors


# ─── I18n ──────────────────────────────────────────────────────────────


def test_tr_default():
    assert tr("OK") == "OK"


def test_set_language_and_translate():
    t = iskg.Translator("es")
    t.load_dict({"OK": "Vale", "Save": "Guardar"})
    set_language("es")
    try:
        assert tr("OK") == "Vale"
        assert tr("Save") == "Guardar"
        # unknown falls back to source
        assert tr("XYZ") == "XYZ"
    finally:
        set_language("en")


def test_format_number_thousands():
    formatted = iskg.format_number(1234567.89, decimals=2)
    assert "1" in formatted and "234" in formatted


def test_available_languages_includes_en():
    set_language("en")
    langs = iskg.available_languages()
    assert "en" in langs


# ─── Pickers ────────────────────────────────────────────────────────────


def test_font_picker_renders():
    fp = FontPicker(font_family="Roboto")
    app = iskg.Application("t")
    app.add(Frame(parent=None).grid_columnconfigure(0, weight=1) or Frame())
    app.add(fp)
    loop = app.test_loop()
    assert "Roboto" in loop.html
    assert "iskg-fp-select" in loop.html


def test_font_picker_setter():
    fp = FontPicker()
    fp.font_family = "Open Sans"
    assert fp.font_family == "Open Sans"


def test_image_picker_renders():
    ip = ImagePicker(src="")
    app = iskg.Application("t")
    app.add(ip)
    loop = app.test_loop()
    assert "iskg-imagepicker" in loop.html


def test_searchctrl_renders():
    sc = SearchCtrl(placeholder="Find…")
    app = iskg.Application("t")
    app.add(sc)
    loop = app.test_loop()
    assert "Find" in loop.html
    assert sc.text == ""


def test_carousel_items():
    c = Carousel(items=["A", "B", "C"], loop=True)
    c.add_item("D")
    assert len(c._items) == 4
    c.next()
    assert c._config_dict["current"] == 1
    c.prev()
    assert c._config_dict["current"] == 0
    c.prev()  # wraps to 3 (loop=True)
    assert c._config_dict["current"] == 3


# ─── Calendar ───────────────────────────────────────────────────────────


def test_calendar_initial_date():
    c = Calendar(date=_dt.date(2026, 8, 27))
    assert c.date == _dt.date(2026, 8, 27)


def test_calendar_navigation():
    c = Calendar(date=_dt.date(2026, 8, 27))
    c.next_month()
    assert c._config_dict["view_month"] == 9
    c.next_month()
    assert c._config_dict["view_month"] == 10
    c.prev_year()
    assert c._config_dict["view_year"] == 2025


def test_time_picker():
    tp = TimePicker(time=_dt.time(14, 30))
    assert tp.time == _dt.time(14, 30)
    tp.time = _dt.time(9, 0)
    assert tp.time == _dt.time(9, 0)


def test_datetime_picker():
    dt = DateTimePicker(datetime=_dt.datetime(2026, 8, 27, 14, 30))
    assert dt.datetime == _dt.datetime(2026, 8, 27, 14, 30)


# ─── Charts ─────────────────────────────────────────────────────────────


def test_barchart_renders():
    bc = BarChart(data=[("A", 1), ("B", 2), ("C", 3)], show_values=True)
    app = iskg.Application("t")
    app.add(bc)
    loop = app.test_loop()
    assert "iskg-barchart" in loop.html
    assert "1" in loop.html


def test_barchart_setter():
    bc = BarChart(data=[("X", 5)])
    bc.data = [("P", 10), ("Q", 20)]
    assert bc.data == [("P", 10.0), ("Q", 20.0)]


def test_piechart_renders():
    pc = PieChart(data=[("A", 30), ("B", 70)])
    app = iskg.Application("t")
    app.add(pc)
    loop = app.test_loop()
    assert "iskg-piechart" in loop.html
    assert "iskg-pc-slice" in loop.html


def test_scatterplot_renders_with_trend():
    sp = ScatterPlot(points=[(1, 1), (2, 4), (3, 9)], show_trend=True)
    app = iskg.Application("t")
    app.add(sp)
    loop = app.test_loop()
    assert "iskg-scatter" in loop.html
    assert "<circle" in loop.html


def test_heatmap_renders():
    hm = Heatmap(matrix=[[1, 2, 3], [4, 5, 6]], cmap="viridis")
    app = iskg.Application("t")
    app.add(hm)
    loop = app.test_loop()
    assert "iskg-heatmap" in loop.html
    # 6 cells
    assert loop.html.count("<rect") >= 6


# ─── Toolbar / MDI / Undo / SystemTray ─────────────────────────────────


def test_toolbar_add_action():
    tb = ToolBar()
    tb.add_action("open", "Open", icon="📂")
    tb.add_separator()
    tb.add_action("save", "Save", checkable=True)
    assert len(tb._actions) == 3


def test_toolbar_set_active():
    tb = ToolBar()
    tb.add_action("a", "A", checkable=True)
    tb.add_action("b", "B", checkable=True)
    tb.set_active("b")
    assert tb._config_dict["active_id"] == "b"


def test_mdi_subwindow_close():
    m = MdiArea()
    s = MdiSubWindow(title="X")
    m.add_subwindow(s)
    assert s._config_dict["open"] is True
    s.close()
    assert s._config_dict["open"] is False


def test_mdi_tile_and_cascade():
    m = MdiArea(width=600, height=400)
    for i in range(4):
        m.add_subwindow(MdiSubWindow(title=f"W{i}"))
    m.tile()
    # Each subwindow has been resized
    for s in m._subs:
        assert s._config_dict["width"] > 0
    m.cascade()
    for i, s in enumerate(m._subs):
        assert s._config_dict["x"] == 20 + i * 24


def test_undo_stack_push_undo_redo():
    s = UndoStack()
    assert not s.can_undo
    assert not s.can_redo
    captured = []

    class C(UndoCommand):
        def __init__(self, v):
            super().__init__(f"set {v}")
            self._v = v

        def undo(self):
            captured.append(("undo", self._v))

        def redo(self):
            captured.append(("redo", self._v))

    s.push(C("a"))
    s.push(C("b"))
    assert s.undo_text == "set b"
    s.undo()
    assert s.can_redo
    s.undo()
    s.redo()
    assert captured == [
        ("redo", "a"),
        ("redo", "b"),
        ("undo", "b"),
        ("undo", "a"),
        ("redo", "a"),
    ]


def test_setattr_command():
    class Obj:
        def __init__(self):
            self.x = 0

    o = Obj()
    cmd = iskg.SetAttrCommand(o, "x", 42)
    cmd.redo()
    assert o.x == 42
    cmd.undo()
    assert o.x == 0


# ─── CommandPalette / PropertyGrid / Markdown / GraphicsView ──────────


def test_command_palette_filter():
    cp = CommandPalette(
        commands=[
            ("file.open", "Open File", "Ctrl+O", lambda: None),
            ("file.save", "Save File", "Ctrl+S", lambda: None),
            ("view.zoom", "Zoom In", "Ctrl++", lambda: None),
        ]
    )
    cp._config_dict["query"] = "file"
    assert len(cp._filtered()) == 2
    cp._config_dict["query"] = "save"
    assert len(cp._filtered()) == 1
    cp._config_dict["query"] = "zoom"
    assert len(cp._filtered()) == 1
    cp._config_dict["query"] = "nope"
    assert len(cp._filtered()) == 0


def test_property_grid_basic():
    class Obj:
        def __init__(self):
            self.name = "alice"
            self.age = 30
            self.active = True

    grid = PropertyGrid(target=Obj())
    html = grid._render()
    assert "name" in html
    assert "alice" in html
    assert "age" in html
    assert "30" in html


def test_property_grid_set_event():
    class Obj:
        name = "x"

    o = Obj()
    grid = PropertyGrid(target=o, properties=["name"])
    grid._handle_bridge_event("set", "name:bob")
    assert o.name == "bob"


def test_markdown_render_basic():
    html = render_markdown("# Title\n\n**bold** and *italic* and `code`")
    assert "<h1>Title</h1>" in html
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html
    assert "<code>code</code>" in html


def test_markdown_render_lists():
    html = render_markdown("- one\n- two\n- three")
    assert "<ul>" in html
    assert "<li>one</li>" in html


def test_markdown_render_link():
    html = render_markdown("[click](https://example.com)")
    assert 'href="https://example.com"' in html
    assert "click</a>" in html


def test_markdown_viewer_widget():
    mv = MarkdownViewer(markdown="# Hi")
    assert mv.markdown == "# Hi"
    mv.markdown = "# Bye"
    assert mv.markdown == "# Bye"


def test_graphics_view_add_remove():
    gv = GraphicsView(width=300, height=200)
    rid = gv.add_item(x=10, y=10, w=40, h=40, label="A")
    assert rid == "item-0"
    rid2 = gv.add_item(kind="ellipse", x=100, y=100, w=50, h=50, label="B")
    assert rid2 == "item-1"
    assert len(gv._items) == 2
    gv.remove_item(rid)
    assert len(gv._items) == 1
    gv.clear()
    assert len(gv._items) == 0


# ─── Display extras ─────────────────────────────────────────────────────


def test_avatar_renders():
    a = Avatar(initials="AB", size=40)
    app = iskg.Application("t")
    app.add(a)
    loop = app.test_loop()
    assert "AB" in loop.html
    assert "iskg-avatar" in loop.html


def test_badge_renders():
    b = Badge(text="NEW", variant="success")
    app = iskg.Application("t")
    app.add(b)
    loop = app.test_loop()
    assert "NEW" in loop.html
    assert "success" in loop.html


def test_badge_invalid_variant_defaults():
    b = Badge(text="x", variant="bogus")
    assert b.variant == "default"


def test_spinner_renders():
    s = Spinner(size=24)
    app = iskg.Application("t")
    app.add(s)
    loop = app.test_loop()
    assert "iskg-spinner" in loop.html


def test_progress_circle_renders():
    pc = ProgressCircle(value=0.5, size=80)
    app = iskg.Application("t")
    app.add(pc)
    loop = app.test_loop()
    assert "iskg-progress-circle" in loop.html
    assert "50%" in loop.html


# ─── Modal ──────────────────────────────────────────────────────────────


def test_modal_show_hide():
    m = Modal(title="Dialog", width=300, height=200)
    assert m.visible is False
    m.show()
    assert m.visible is True
    m.hide()
    assert m.visible is False


# ─── FileBrowser (already in 0.4.7) ────────────────────────────────────


def test_filebrowser_root_setter():
    fb = FileBrowser(root="/tmp")
    assert fb.root == "/tmp"
    fb.root = "/var"
    assert fb.root == "/var"


# ─── Debug / Logger ────────────────────────────────────────────────────


def test_qdebug_prints(capsys):
    qDebug("hello")
    out = capsys.readouterr()
    assert "[ISKG:debug]" in out.err
    assert "hello" in out.err


def test_logger_level_filtering(capsys):
    log = Logger(level="warning")
    log.info("ignored")
    log.warning("shown")
    out = capsys.readouterr()
    assert "ignored" not in out.err
    assert "shown" in out.err


def test_logger_history():
    log = Logger(level="debug")
    log.info("first")
    log.info("second")
    assert any("first" in h[2] for h in log.history)
    assert any("second" in h[2] for h in log.history)
