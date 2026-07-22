def test_all_widgets_importable():
    from iskg import (
        Label,
        Button,
        Entry,
        CheckBox,
        RadioButton,
        ComboBox,
        Slider,
        ProgressBar,
        Frame,
        ListBox,
        ScrollBar,
        Text,
        SpinBox,
        Separator,
        Notebook,
        Canvas,
        Scale,
        MessageDialog,
        Knob,
        LEDDisplay,
        DataGrid,
        IndicatorLED,
        RadialGauge,
        ToggleSwitch,
        StatusBar,
        Tooltip,
        Spacer,
        ImageBox,
        IconLabel,
        RichText,
        TreeView,
        DropTarget,
        MenuBar,
        FileDialog,
        Application,
        Widget,
        VERSION,
    )

    assert VERSION == "0.3.10"
    assert issubclass(Button, Widget)


def test_widgets_subpackage_exports_menu():
    from iskg.widgets import Menu, MenuItem

    assert Menu is not None
    assert MenuItem is not None
