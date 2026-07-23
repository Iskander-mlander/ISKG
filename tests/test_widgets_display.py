from iskg import IndicatorLED, Label, LEDDisplay, ProgressBar, RadialGauge, StatusBar


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
