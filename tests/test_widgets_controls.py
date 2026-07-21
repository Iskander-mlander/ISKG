from iskg import (
    Button,
    Entry,
    CheckBox,
    RadioButton,
    ComboBox,
    Slider,
    SpinBox,
    Scale,
    ToggleSwitch,
)


class TestButton:
    def test_create(self):
        b = Button(text="Click")
        assert b.text == "Click"

    def test_text_setter(self):
        b = Button(text="A")
        b.text = "B"
        assert b.text == "B"

    def test_render_html(self):
        b = Button(text="Test")
        html = b._render()
        assert 'id="' in html
        assert "iskg-btn" in html
        assert "Test" in html

    def test_command(self):
        calls = []
        b = Button(text="X", command=lambda: calls.append(1))
        b._handle_bridge_event("click", None)
        assert calls == [1]


class TestEntry:
    def test_create(self):
        e = Entry(text="hello")
        assert e.text == "hello"

    def test_text_setter(self):
        e = Entry(text="a")
        e.text = "b"
        assert e.text == "b"

    def test_render_html(self):
        e = Entry(text="val")
        html = e._render()
        assert "iskg-entry" in html
        assert 'value="val"' in html

    def test_password(self):
        e = Entry(text="secret", password=True)
        html = e._render()
        assert 'type="password"' in html


class TestCheckBox:
    def test_create_checked(self):
        cb = CheckBox(text="Enable", checked=True)
        assert cb.checked is True
        assert cb.text == "Enable"

    def test_toggle(self):
        cb = CheckBox(text="X")
        cb.checked = True
        assert cb.checked is True
        cb.checked = False
        assert cb.checked is False

    def test_render_html(self):
        cb = CheckBox(text="Opt", checked=True)
        html = cb._render()
        assert "iskg-check-wrap" in html
        assert "checked" in html


class TestRadioButton:
    def test_create(self):
        rb = RadioButton(text="A", value="a")
        assert rb.text == "A"
        assert rb.value == "a"
        assert rb.selected is False

    def test_select(self):
        rb = RadioButton(text="A", value="a")
        rb.selected = True
        assert rb.selected is True

    def test_render_html(self):
        rb = RadioButton(text="Opt", value="x")
        html = rb._render()
        assert "iskg-radio-wrap" in html


class TestComboBox:
    def test_create(self):
        cb = ComboBox(values=["A", "B", "C"], current=1)
        assert cb.value == "B"
        assert cb.current == 1

    def test_change_current(self):
        cb = ComboBox(values=["A", "B"], current=0)
        cb.current = 1
        assert cb.value == "B"

    def test_render_html(self):
        cb = ComboBox(values=["X", "Y"])
        html = cb._render()
        assert "iskg-cb-wrap" in html


class TestSlider:
    def test_create(self):
        s = Slider(from_=0, to=100, value=50)
        assert s.value == 50

    def test_value_setter(self):
        s = Slider(from_=0, to=100)
        s.value = 75
        assert s.value == 75

    def test_render_horizontal(self):
        s = Slider(value=50, width=200)
        html = s._render()
        assert 'type="range"' in html
        assert "iskg-slider-wrap" in html

    def test_render_vertical(self):
        s = Slider(value=50, orient="vertical")
        html = s._render()
        assert "iskg-slider-vert" in html


class TestSpinBox:
    def test_create(self):
        sp = SpinBox(from_=0, to=10, value=5)
        assert sp.value == 5

    def test_value_setter(self):
        sp = SpinBox(from_=0, to=10)
        sp.value = 7
        assert sp.value == 7

    def test_render_html(self):
        sp = SpinBox(value=3)
        html = sp._render()
        assert "iskg-spinbox-wrap" in html


class TestScale:
    def test_create(self):
        sc = Scale(from_=0, to=100, value=50)
        assert sc.value == 50

    def test_render_html(self):
        sc = Scale(value=50)
        html = sc._render()
        assert "iskg-scale-wrap" in html


class TestToggleSwitch:
    def test_create(self):
        ts = ToggleSwitch(text="Arm", checked=True)
        assert ts.checked is True

    def test_toggle(self):
        ts = ToggleSwitch(text="X")
        ts.checked = True
        assert ts.checked is True

    def test_render_html(self):
        ts = ToggleSwitch(text="Mode", checked=True)
        html = ts._render()
        assert "iskg-toggle-wrap" in html
