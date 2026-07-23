def test_all_widgets_importable():
    from iskg import (
        VERSION,
        Button,
        Widget,
    )

    assert VERSION == "0.3.11"
    assert issubclass(Button, Widget)


def test_widgets_subpackage_exports_menu():
    from iskg.widgets import Menu, MenuItem

    assert Menu is not None
    assert MenuItem is not None
