from iskg import (
    IconLabel,
    ImageBox,
    IndicatorLED,
    Label,
    LEDDisplay,
    ProgressBar,
    RadialGauge,
    StatusBar,
)


class TestLabel:
    def test_create(self):
        lbl = Label(text="Hello")
        assert lbl.text == "Hello"

    def test_text_setter(self):
        lbl = Label(text="A")
        lbl.text = "B"
        assert lbl.text == "B"

    def test_render_html(self):
        lbl = Label(text="Test")
        html = lbl._render()
        assert "iskg-label" in html
        assert "Test" in html

    def test_wraplength(self):
        lbl = Label(text="X", wraplength=100)
        assert lbl.wraplength == 100
        html = lbl._render()
        assert "max-width:100px" in html

    def test_wraplength_none(self):
        lbl = Label(text="X")
        lbl.wraplength = None
        assert lbl.wraplength is None

    def test_anchor_center(self):
        lbl = Label(text="X", anchor="center")
        assert lbl.anchor == "center"
        html = lbl._render()
        assert "text-align:center" in html

    def test_anchor_right(self):
        lbl = Label(text="X", anchor="e")
        html = lbl._render()
        assert "text-align:right" in html

    def test_justify_init(self):
        lbl = Label(text="X", justify="center")
        assert lbl.justify == "center"
        html = lbl._render()
        assert "text-align:center" in html

    def test_color_class(self):
        lbl = Label(text="X", color="red")
        html = lbl._render()
        assert "red" in html

    def test_click_binding(self):
        lbl = Label(text="X")
        lbl.bind("click", lambda d: None)
        html = lbl._render()
        assert "onclick" in html


class TestProgressBar:
    def test_create(self):
        pb = ProgressBar(value=50)
        assert pb.value == 50

    def test_value_setter(self):
        pb = ProgressBar(value=10)
        pb.value = 80
        assert pb.value == 80

    def test_render_html(self):
        pb = ProgressBar(value=75, width=200, show_text=True)
        html = pb._render()
        assert "iskg-progress-wrap" in html
        assert "75%" in html or "75" in html


class TestLEDDisplay:
    def test_create(self):
        led = LEDDisplay(value=42, digits=3, color="green")
        assert led.value == 42

    def test_render_html(self):
        led = LEDDisplay(value=123, digits=4)
        html = led._render()
        assert "iskg-led-wrap" in html
        assert "0123" in html

    def test_value_setter(self):
        led = LEDDisplay(value=10)
        led.value = 99
        assert led.value == 99


class TestIndicatorLED:
    def test_create(self):
        ind = IndicatorLED(color="green", active=True, label="OK")
        assert ind.active is True

    def test_toggle(self):
        ind = IndicatorLED(active=True)
        ind.active = False
        assert ind.active is False

    def test_render_html(self):
        ind = IndicatorLED(color="red", active=True, label="Alarm")
        html = ind._render()
        assert "iskg-indicator" in html


class TestRadialGauge:
    def test_create(self):
        g = RadialGauge(from_=0, to=100, value=50, size=80)
        assert g.value == 50

    def test_value_setter(self):
        g = RadialGauge(value=10)
        g.value = 90
        assert g.value == 90

    def test_render_html(self):
        g = RadialGauge(value=75, size=80, label="TEST")
        html = g._render()
        assert "iskg-gauge-wrap" in html


class TestStatusBar:
    def test_create(self):
        sb = StatusBar(sections=[{"text": "READY", "color": "green"}])
        html = sb._render()
        assert "iskg-statusbar" in html
        assert "READY" in html

    def test_text_getter_first_section(self):
        sb = StatusBar(sections=[{"text": "ONE"}, {"text": "TWO"}])
        assert sb.text == "ONE"

    def test_text_setter_updates_first_section(self):
        sb = StatusBar(sections=[{"text": "OLD"}])
        sb.text = "NEW"
        assert sb._config_dict["sections"][0]["text"] == "NEW"

    def test_text_setter_empty_sections(self):
        sb = StatusBar(sections=[])
        sb.text = "NEW"
        assert sb._config_dict["sections"][0]["text"] == "NEW"

    def test_section_as_string(self):
        sb = StatusBar(sections=["plain"])
        html = sb._render()
        assert "plain" in html


class TestIconLabel:
    def test_create(self):
        il = IconLabel(text="Test", icon="🔥", color="red")
        html = il._render()
        assert "iskg-iconlabel" in html
        assert "🔥" in html

    def test_svg_icon(self):
        il = IconLabel(text="X", icon="<svg></svg>")
        html = il._render()
        assert "svg" in html


class TestImageBox:
    def test_command_cursor(self):
        img = ImageBox(src="data:,", command=lambda: None)
        html = img._render()
        assert "cursor:pointer" in html
