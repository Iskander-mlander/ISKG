"""Smoke tests that exercise the example apps' *rendering*, not just import.

For every ``examples/*.py`` module that exposes ``build_app()``, we build the
app headlessly (no window) and assert that the generated HTML contains the id
of every widget in the tree. This catches demos that construct widgets but fail
to render them (e.g. a misconfigured widget that drops out of the DOM).
"""

import glob
import importlib
import os

import pytest

from iskg import Application

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")

EXAMPLE_MODULES = sorted(
    os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(EXAMPLE_DIR, "*.py"))
)


def _collect_ids(widget: object, out: list[str]) -> None:
    out.append(widget._id)  # type: ignore[attr-defined]
    for child in widget._children:  # type: ignore[attr-defined]
        _collect_ids(child, out)


@pytest.mark.parametrize("mod_name", EXAMPLE_MODULES, ids=EXAMPLE_MODULES)
def test_example_build_app_renders_widgets(mod_name: str) -> None:
    mod = importlib.import_module("examples." + mod_name)
    if not hasattr(mod, "build_app"):
        pytest.skip(f"{mod_name} no expone build_app()")

    app = mod.build_app()
    assert isinstance(app, Application)

    html = app._build_html()
    ids: list[str] = []
    for root in app._root_widgets:
        _collect_ids(root, ids)

    assert ids, f"{mod_name}: build_app() no añadió ningún widget"

    for wid in ids:
        assert wid in html, f"{mod_name}: el widget {wid} no aparece en el HTML"
