from typing import cast

from iskg import Canvas, IconLabel, ImageBox, Knob, RichText, Text, Tooltip


class TestText:
    def test_create(self):
        t = Text(text="hello")
        assert t.text == "hello"

    def test_append(self):
        t = Text(text="a")
        t.append("b")
        assert t.text == "ab"

    def test_clear(self):
        t = Text(text="content")
        t.clear()
        assert t.text == ""

    def test_render_html(self):
        t = Text(text="Hello\nWorld", width=200, height=100)
        html = t._render()
        assert "iskg-text" in html
        assert "textarea" in html


class TestRichText:
    def test_create(self):
        rt = RichText(text="<b>bold</b>")
        html = rt._render()
        assert "iskg-richtext-wrap" in html
        assert "iskg-richtext-toolbar" in html

    def test_no_toolbar(self):
        rt = RichText(text="text", show_toolbar=False)
        html = rt._render()
        assert "iskg-richtext-toolbar" not in html


class TestCanvas:
    def test_create(self):
        c = Canvas(width=300, height=200)
        html = c._render()
        assert "iskg-canvas" in html
        assert 'width="300"' in html

    def test_clear(self):
        c = Canvas()
        c.create_rectangle(10, 10, 50, 50)
        assert len(c._draw_commands) == 1
        c.clear()
        assert len(c._draw_commands) == 0


class TestKnob:
    def test_create(self):
        k = Knob(from_=0, to=100, value=50, size=60, color="cyan")
        assert k.value == 50

    def test_value_setter(self):
        k = Knob(value=10)
        k.value = 80
        assert k.value == 80

    def test_render_html(self):
        k = Knob(value=50, size=60)
        html = k._render()
        assert "iskg-knob-wrap" in html
        assert "iskg-knob-canvas" in html


class TestTooltip:
    def test_create(self):
        t = Tooltip(text="Help", delay=300)
        js = t.attach("some_id")
        assert "iskg-tooltip" in js
        assert "some_id" in js

    def test_render_empty(self):
        t = Tooltip(text="X")
        assert t._render() == ""
        assert t._render_js() == ""


class TestImageBox:
    def test_create(self):
        img = ImageBox(src="test.png", width=50, height=50)
        html = img._render()
        assert "iskg-imagebox" in html
        assert 'src="test.png"' in html


class TestIconLabel:
    def test_create(self):
        il = IconLabel(text="Armed", icon="⚡", icon_size=14)
        html = il._render()
        assert "iskg-iconlabel" in html
        assert "Armed" in html
        assert "⚡" in html


class TestTooltipOnWidgets:
    def test_property_default(self):
        from iskg import Widget

        w = Widget()
        assert w.tooltip == ""

    def test_property_set(self):
        from iskg import Widget

        w = Widget()
        w.tooltip = "Hello"
        assert w.tooltip == "Hello"

    def test_config_keyword(self):
        from iskg import Widget

        w = Widget(tooltip="Init tip")
        assert w.tooltip == "Init tip"

    def test_config_method(self):
        from iskg import Widget

        w = Widget()
        w.config(tooltip="Config tip")
        assert w.tooltip == "Config tip"

    def test_js_generated(self):
        from iskg.widgets._controls import Button

        w = Button(text="OK", tooltip="Click me")
        assert "mouseenter" in w._render_tooltip_js()
        assert "Click me" in w._render_tooltip_js()

    def test_js_empty_when_no_tooltip(self):
        from iskg.widgets._controls import Button

        w = Button(text="OK")
        assert w._render_tooltip_js() == ""

    def test_build_html_includes_tooltip(self):
        from iskg import Widget
        from iskg.template import build_html
        from iskg.theme import IFAZ_CSS

        btn = Widget()
        btn.tooltip = "Global tip"
        html = build_html([btn], IFAZ_CSS)
        assert "Global tip" in html


class TestTimerAfter:
    def test_after_cancel(self):
        from iskg import Widget

        w = Widget()
        called = []
        t = w.after(10000, lambda: called.append(1))
        assert t.running is True
        t.cancel()
        assert t.running is False

    def test_after_immediate(self):
        from iskg import Widget

        w = Widget()
        called = []
        t = w.after(1, lambda: called.append(1))
        import time

        time.sleep(0.05)
        t.cancel()
        # Timer already fired, .running stays True (timer can't stop once fired)

    def test_after_cancel_legacy(self):
        from iskg import Widget

        w = Widget()
        called = []
        t = w.after(10000, lambda: called.append(1))
        w.after_cancel(t._id)
        assert t.running is False


class TestGridImprovements:
    def test_center_sticky(self):
        from iskg import Widget

        w = Widget()
        w.grid(row=0, column=0, sticky="c")
        style = w._render_style()
        assert "justify-self:center" in style
        assert "align-self:center" in style

    def test_center_horizontal_only(self):
        from iskg import Widget

        w = Widget()
        w.grid(row=0, column=0, sticky="cw")
        style = w._render_style()
        assert "justify-self:start" in style  # 'w' wins over 'c'
        assert "align-self:center" in style  # 'c' used for vertical

    def test_minsize_in_grid_template(self):
        from iskg.widgets._containers import _grid_template

        d = cast("dict[int, tuple[float, int]]", {0: (2, 100), 2: (1, 50)})
        result = _grid_template(d, 3)
        assert "minmax(100px,2fr)" in result
        assert "minmax(50px,1fr)" in result

    def test_grid_columnconfigure_minsize(self):
        from iskg.widgets._containers import Frame

        f = Frame()
        f.grid_columnconfigure(0, weight=2, minsize=100)
        assert f._grid_column_weights[0] == (2, 100)
        f.grid_columnconfigure(0, weight=0, minsize=0)
        assert 0 not in f._grid_column_weights
