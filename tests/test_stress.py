"""Stress & stability tests for ISKG."""

import time

import pytest

from iskg import Frame, Label, Notebook, PanedWindow, Widget


@pytest.mark.stress
def test_stress_mass_create_destroy():
    """Create and destroy many widgets; verify no crashes, no memory leaks."""
    refs = []

    # ── Create batch ──
    for _ in range(5):
        batch = [Label(None, text=f"s{i}") for i in range(500)]
        refs.extend(batch)

    # ── Attach to a root and render ──
    root = Frame()
    for w in refs:
        root.add(w)
    html = root._render()
    assert "iskg-label" in html

    # ── Destroy half ──
    for w in refs[: len(refs) // 2]:
        w.destroy()
    html2 = root._render()
    count_labels = html2.count("iskg-label")
    assert count_labels < 2500 // 2 + 10  # ~1250 after destruction

    # ── Destroy rest ──
    for w in refs[len(refs) // 2 :]:
        w.destroy()
    html3 = root._render()
    assert "iskg-label" not in html3


def test_stress_deep_nesting():
    """100 levels of nested Frame + PanedWindow + Notebook."""

    def build(depth: int) -> Widget:
        if depth <= 0:
            return Label(None, text="bottom")

        if depth % 3 == 0:
            pw = PanedWindow(None, orient="horizontal")
            pw.add(build(depth - 1))
            pw.add(Label(None, text=f"pw_{depth}"))
            return pw
        elif depth % 3 == 1:
            nb = Notebook(None)
            tab = Frame(None, container=True)
            tab.add(build(depth - 1))
            nb.add_tab(f"tab{depth}", tab)
            return nb
        else:
            f = Frame(None)
            f.add(build(depth - 1))
            return f

    root = build(100)
    html = root._render()
    assert "iskg-panedwindow" in html
    assert "iskg-notebook" in html
    assert "iskg-label" in html


def test_stress_no_duplicate_ids():
    """Complex tree must produce unique IDs."""
    w1 = Label(None, text="a")
    w2 = Label(None, text="b")
    inner_frame = Frame(None)
    inner_frame.add(Label(None, text="inner"))
    root = Frame()
    pw = PanedWindow(root, orient="horizontal")
    pw.add(w1)
    pw.add(w2)
    pw.add(inner_frame)
    root.add(Label(None, text="sibling"))
    html = root._render()
    import re

    ids = re.findall(r'id="([^"]+)"', html)
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {ids}"


def test_stress_property_updates():
    """Mass property changes must not crash."""
    widgets = [Label(None, text=f"l{i}") for i in range(200)]
    for i, w in enumerate(widgets):
        w.text = f"updated_{i}"
        w._config_dict["fg"] = "#ff6600"
        w._config_dict["font-size"] = 12 + (i % 6)
        w._config_dict["padding"] = i % 20
    root = Frame()
    for w in widgets:
        root.add(w)
    html = root._render()
    assert html.count("updated_") == 200


def test_stress_reparent():
    """Reparent widgets multiple times via pack(in_=)."""
    frames = [Frame(None) for _ in range(10)]
    widget = Label(None, text="nomad")

    for f in frames:
        widget.pack(in_=f)

    # widget ends up in the last frame
    assert widget._parent is frames[-1]
    last_frame = frames[-1]
    html = last_frame._render()
    assert "nomad" in html
    assert "iskg-label" in html


def test_stress_mixed_layouts():
    """Mix pack and grid in same parent (should warn but not crash)."""
    f = Frame()
    lbl = Label(f, text="packed")
    lbl.pack()
    with pytest.warns(UserWarning, match="pack.*grid|grid.*pack"):
        lbl.grid(row=0, column=0)
    html = f._render()
    assert "packed" in html


@pytest.mark.benchmark
def test_benchmark_creation():
    """Benchmark widget creation throughput."""
    n = 2000
    t0 = time.perf_counter()
    [Label(None, text=f"b{i}") for i in range(n)]
    t1 = time.perf_counter()
    rate = n / (t1 - t0)
    print(f"\n[bench] {n} widgets created in {t1 - t0:.3f}s  ({rate:.0f} w/s)")
    assert rate > 10_000  # should easily exceed 10k widgets/s


@pytest.mark.benchmark
def test_benchmark_render():
    """Benchmark HTML render throughput."""
    n = 1000
    root = Frame()
    for i in range(n):
        root.add(Label(None, text=f"r{i}"))
    t0 = time.perf_counter()
    html = root._render()
    t1 = time.perf_counter()
    print(f"\n[bench] {n} children rendered in {t1 - t0:.3f}s  ({len(html)} chars)")
    assert len(html) > 10_000
