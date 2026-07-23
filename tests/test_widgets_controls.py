from iskg import (
    Button,
    CheckBox,
    ComboBox,
    Entry,
    RadioButton,
    Scale,
    Slider,
    SpinBox,
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

    def test_variant_css_class(self):
        b = Button(text="Danger", variant="danger")
        html = b._render()
        assert "danger" in html

    def test_size_css_class(self):
        b = Button(text="Small", size="sm")
        html = b._render()
        assert "sm" in html

    def test_width_in_style(self):
        b = Button(text="Wide", width=200)
        html = b._render()
        assert "width:200px" in html


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

    def test_justify_init(self):
        e = Entry(text="a", justify="center")
        assert e.justify == "center"

    def test_justify_setter(self):
        e = Entry(text="a")
        e.justify = "right"
        assert e.justify == "right"

    def test_maxlength_init(self):
        e = Entry(text="a", maxlength=10)
        assert e.maxlength == 10

    def test_maxlength_setter(self):
        e = Entry(text="a")
        e.maxlength = 5
        assert e.maxlength == 5
        e.maxlength = None
        assert e.maxlength is None

    def test_justify_center_render(self):
        e = Entry(text="a", justify="center")
        html = e._render()
        assert "text-align:center" in html

    def test_justify_right_render(self):
        e = Entry(text="a", justify="right")
        html = e._render()
        assert "text-align:right" in html


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

    def test_disabled_class(self):
        cb = CheckBox(text="X", disabled=True)
        html = cb._render()
        assert "disabled" in html


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

    def test_disabled_class(self):
        ts = ToggleSwitch(text="X", disabled=True)
        html = ts._render()
        assert "disabled" in html


class TestRadioButtonExtended:
    def test_command_init(self):
        rb = RadioButton(text="X", command=lambda: None)
        assert rb._config_dict.get("command") is not None

    def test_disabled_class(self):
        rb = RadioButton(text="X", disabled=True)
        html = rb._render()
        assert "disabled" in html


class TestComboBoxExtended:
    def test_editable(self):
        cb = ComboBox(values=["A", "B"], current=0, editable=True)
        html = cb._render()
        assert "<input" in html

    def test_non_editable(self):
        cb = ComboBox(values=["A", "B"], current=0)
        html = cb._render()
        assert "<input" not in html


class TestSliderExtended:
    def test_init_with_min_max(self):
        s = Slider(from_=0, to=100, value=50, min_value=10, max_value=90)
        assert s._config_dict.get("from") == 10
        assert s._config_dict.get("to") == 90


class TestSpinBoxExtended:
    def test_init_with_min_max(self):
        sp = SpinBox(from_=0, to=100, value=50, min_value=10, max_value=90)
        assert sp._config_dict.get("from") == 10
        assert sp._config_dict.get("to") == 90


class TestScaleExtended:
    def test_vertical_render(self):
        sc = Scale(value=50, orient="vertical")
        html = sc._render()
        assert "iskg-slider-vert" in html
