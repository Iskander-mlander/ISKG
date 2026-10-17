"""Content-minimum propagation, fit=False opt-out and window min_size."""

from __future__ import annotations

from iskg.app import Application
from iskg.metrics import (
    BUTTON_HEIGHT,
    BUTTON_LG_HEIGHT,
    BUTTON_SM_HEIGHT,
    ENTRY_HEIGHT,
    ENTRY_WIDTH,
    estimate_text_width,
)
from iskg.widgets._containers import (
    Frame,
    Notebook,
    PanedWindow,
    ScrolledFrame,
)
from iskg.widgets._controls import Button, CheckBox, Entry
from iskg.widgets._display import Label


class TestLeafMins:
    def test_button_default(self):
        assert Button(text="OK")._content_min_size() == (
            estimate_text_width("OK", 12, pad_x=16, letter_spacing=1, extra=2),
            BUTTON_HEIGHT,
        )

    def test_button_size_variants(self):
        assert Button(text="OK", size="sm")._content_min_size()[1] == BUTTON_SM_HEIGHT
        assert Button(text="OK", size="lg")._content_min_size()[1] == BUTTON_LG_HEIGHT

    def test_button_explicit_width_wins(self):
        w = Button(text="OK", width=300)._content_min_size()[0]
        assert w == 300

    def test_entry_default(self):
        assert Entry()._content_min_size() == (ENTRY_WIDTH, ENTRY_HEIGHT)

    def test_entry_explicit_width_raises_min(self):
        assert Entry(width=320)._content_min_size()[0] == 320

    def test_label_multiline_height(self):
        h = Label(text="a\nb\nc")._content_min_size()[1]
        assert h > Label(text="a")._content_min_size()[1]

    def test_checkbox_includes_box_and_text(self):
        w, h = CheckBox(text="Toggle")._content_min_size()
        assert w > estimate_text_width("Toggle", 11, pad_x=6)
        assert h == 22


class TestFramePropagation:
    def _frame_with_button(self, **frame_kwargs) -> Frame:
        f = Frame(**frame_kwargs)
        b = Button(text="ACEPTAR")
        b.pack()
        f.add(b)
        return f

    def test_pack_column_adds_chrome(self):
        f = self._frame_with_button()
        bw, bh = Button(text="ACEPTAR")._content_min_size()
        # chrome 14px each side + header 20px (text=""):
        assert f._content_min_size() == (bw + 14, bh + 14)

    def test_header_adds_height(self):
        f = self._frame_with_button(text="Panel")
        bw, bh = Button(text="ACEPTAR")._content_min_size()
        assert f._content_min_size() == (bw + 14, bh + 34)

    def test_pack_row_sums_widths(self):
        f = Frame()
        for label in ("AA", "BBBB", "C"):
            b = Button(text=label)
            b.pack(side="left")
            f.add(b)
        w, _ = f._content_min_size()
        expect = sum(Button(text=t)._content_min_size()[0] for t in ("AA", "BBBB", "C"))
        expect += 3 * 2  # default gap between 3 children
        assert w == expect + 14

    def test_place_uses_bounds(self):
        f = Frame(container=False)
        b = Button(text="HOLA")
        b.place(x=100, y=50)
        f.add(b)
        bw, bh = b._content_min_size()
        assert f._content_min_size() == (100 + bw + 14, 50 + bh + 14)

    def test_grid_column_max(self):
        f = Frame()
        for i, text in enumerate(("AA", "BBBBBB")):
            b = Button(text=text)
            b.grid(row=0, column=i)
            f.add(b)
        w, _ = f._content_min_size()
        cols = [
            Button(text="AA")._content_min_size()[0],
            Button(text="BBBBBB")._content_min_size()[0],
        ]
        assert w == sum(cols) + 3 + 14  # one gap + chrome

    def test_hidden_children_skipped(self):
        f = Frame()
        b = Button(text="ACEPTAR")
        b.pack()
        b.config(hidden=True)
        f.add(b)
        assert f._content_min_size() == (14, 14)


class TestFitOptOut:
    def test_fit_false_returns_zero(self):
        f = Frame(fit=False)
        b = Button(text="ACEPTAR")
        b.pack()
        f.add(b)
        assert f._content_min_size() == (0, 0)

    def test_fit_false_render_keeps_old_zeros(self):
        f = Frame(fit=False)
        b = Button(text="X")
        b.pack(expand=True)
        f.add(b)
        html = f._render()
        # frame element and wrapper keep the old blanket zeros
        assert "min-height:0" in html
        assert "min-height:0;min-width:0" in html
        # the frame imposes no minimum, even with children
        assert f._content_min_size() == (0, 0)
        # children keep their own protection (fit is per-widget)
        assert "min-width:0px" not in b._render_style()

    def test_fit_false_expanded_child(self):
        f = Frame()
        b = Button(text="X")
        b.pack(expand=True)
        b.config(fit=False)
        f.add(b)
        assert "min-width:0px;min-height:0px" in b._render_style()

    def test_explicit_min_width_css_wins(self):
        b = Button(text="OK", min_width=500)
        b.pack(expand=True)
        style = b._render_style()
        # computed min comes from the expand branch; config CSS is appended
        # last, so the explicit min_width overrides it
        assert style.index("min-width:500px") > style.index("min-width:")
        assert style.endswith("min-width:500px;")


class TestScrolledFrame:
    def test_content_does_not_propagate(self):
        sf = ScrolledFrame()
        b = Button(text="VERY LONG TEXT")
        b.pack()
        sf.add(b)
        assert sf._content_min_size() == (0, 0)

    def test_explicit_viewport_counts(self):
        assert ScrolledFrame(width=400, height=200)._content_min_size() == (400, 200)


class TestNotebookAndPaned:
    def test_notebook_uses_widest_page_plus_tabbar(self):
        nb = Notebook()
        for title, text in (("A", "AA"), ("B", "BBBBBBBB")):
            page = Frame(container=False)
            b = Button(text=text)
            b.pack()
            page.add(b)
            nb.add_tab(title, page)
        w, h = nb._content_min_size()
        assert w == Button(text="BBBBBBBB")._content_min_size()[0] + 14
        assert h == Button(text="BBBBBB")._content_min_size()[1] + 14 + 28

    def test_paned_sums_panes_and_sashes(self):
        pw = PanedWindow(orient="horizontal", minsize=40)
        for text in ("AAAA", "BB"):
            pane = Frame(container=False)
            b = Button(text=text)
            b.pack()
            pane.add(b)
            pw.add(pane)
        w, _ = pw._content_min_size()
        a = max(40, Button(text="AAAA")._content_min_size()[0] + 14)
        bmin = max(40, Button(text="BB")._content_min_size()[0] + 14)
        assert w == a + bmin + 5  # one sash


class TestWindowMin:
    def _app_with_frame(self, **app_kwargs) -> tuple[Application, Frame]:
        app = Application("t", **app_kwargs)
        f = Frame(text="Panel")
        app.add(f)
        b = Button(text="ACEPTAR")
        b.pack(expand=True)
        f.add(b)
        e = Entry()
        e.pack()
        f.add(e)
        return app, f

    def test_window_min_matches_content(self):
        app, f = self._app_with_frame()
        app.test_loop()
        assert app.window_min_size == f._content_min_size()

    def test_window_min_width_is_max_height_is_sum(self):
        app = Application("t")
        f1 = Frame(text="One")
        f1.add(Button(text="AAAA"))
        f2 = Frame(text="Two")
        f2.add(Button(text="BBBBBBBBBB"))
        app.add(f1)
        app.add(f2)
        app.test_loop()
        w1, h1 = f1._content_min_size()
        w2, h2 = f2._content_min_size()
        assert app.window_min_size == (max(w1, w2), h1 + h2)

    def test_min_size_flag_disables(self):
        app, _ = self._app_with_frame(min_size=False)
        app.test_loop()
        assert app.window_min_size is None

    def test_empty_app_has_no_min(self):
        app = Application("t")
        app.test_loop()
        assert app.window_min_size is None


class TestMetrics:
    def test_estimate_longest_line(self):
        assert estimate_text_width("ab") < estimate_text_width("abcdefgh")

    def test_estimate_padding(self):
        base = estimate_text_width("abc", pad_x=0)
        assert estimate_text_width("abc", pad_x=10) == base + 20
