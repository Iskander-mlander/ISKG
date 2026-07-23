def test_all_widgets_importable():
    from iskg import __version__, VERSION, Button, Widget

    assert VERSION == __version__
    assert VERSION is not None
    assert isinstance(VERSION, str)
    assert issubclass(Button, Widget)


def test_widgets_subpackage_exports_menu():
    from iskg.widgets import Menu, MenuItem

    assert Menu is not None
    assert MenuItem is not None
