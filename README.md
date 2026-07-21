<div align="center">
  <img src="iskg/examples/icon.png" width="80" alt="ISKG logo"/>
  <h1>ISKG</h1>
  <p><b>IFAZ Widget Toolkit</b> — Python GUI framework with a tactical/IFAZ theme</p>

  [![CI](https://img.shields.io/github/actions/workflow/status/Iskander-mlander/ISKG/ci.yml?branch=main&label=CI&logo=github)](https://github.com/Iskander-mlander/ISKG/actions)
  [![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python)](https://www.python.org)
  [![License](https://img.shields.io/github/license/Iskander-mlander/ISKG?color=green)](LICENSE)
  [![PyPI](https://img.shields.io/badge/pypi-0.3.7-orange?logo=pypi)](https://pypi.org/project/iskg/)
  [![Platform](https://img.shields.io/badge/platform-linux%20|%20windows%20|%20macos-lightgrey)](#)
</div>

---

**ISKG** renders native-looking widgets as HTML/CSS/JS inside a native window via [pywebview](https://github.com/r0x0r/pywebview). No browser, no HTTP server — just a Python process and a lightweight WebView.

## Features

- **30+ widgets**: Button, Entry, ComboBox, Slider, ProgressBar, Canvas, TreeView, DataGrid, Knob, Gauge, Notebook, MenuBar, and more.
- **Layout engines**: `pack`, `grid` (with sticky + weights), `place`.
- **Theming**: 5 built-in themes (ifaz, amber, green, blue, light), CSS variable system.
- **Cross-platform**: Linux, Windows, macOS (same codebase).
- **Zero HTTP**: No server, no ports, no browser tabs — just a window.
- **JS bridge**: Bidirectional Python ↔ JavaScript calls for real-time UI updates.
- **`.tooltip` on every widget**: Set a tooltip via property or `config()`.
- **`after()` timers**: Cancelable timer objects with `.cancel()` and `.running`.
- **Sphinx docs**: Full API reference [available](docs/_build/html/).

## Comparison — lightness & footprint

| Framework | Dependencies | Installed size | Own code | Notes |
|-----------|-------------|----------------|----------|-------|
| **Tkinter** | 0 (stdlib) | ~1 MB | — | No modern widgets, dated look |
| **Remi** | 1 (bottle/werkzeug) | ~2 MB | ~15 KLoC | Browser-based, needs a tab |
| **ISKG** | 3 (pywebview, bottle, proxy_tools) | ~2 MB | ~6 KLoC | Native window, modern widgets |
| **PySimpleGUI** | 1 (tkinter/Qt) | ~5 MB | ~100 KLoC | Wrapper, not a framework |
| **Dear PyGui** | 0 (bundled) | ~10 MB | ~80 KLoC | GPU-accelerated, no native look |
| **Kivy** | SDL2, GLEW, etc | ~15 MB | ~200 KLoC | Own UI language, heavy |
| **wxPython** | wxWidgets | ~20 MB | ~150 KLoC | Native look, complex build |
| **PyQt/PySide** | Qt (~100 MB) | ~50 MB | ~500 KLoC | Full-featured, huge size |
| **NiceGUI** | FastAPI + uvicorn + Vue | ~30 MB | ~50 KLoC | Browser-based, async |
| **Flet** | Flutter SDK | ~200 MB | — | Requires Flutter toolchain |

**ISKG ranks 3rd** in lightness — only Tkinter and Remi are smaller. Among frameworks that render in a **native window** (not a browser tab), ISKG is the **lightest after Tkinter**.

## Quick start

```bash
pip install iskg
```

```python
from iskg import Application, Button, Label, Frame

app = Application(title="Hello ISKG", width=400, height=300)

def on_click(data):
    label.config(text="Button clicked!")

frame = Frame()
Label(parent=frame, text="Welcome to ISKG")
Button(parent=frame, text="Click me", command=on_click)

app.run()
```

## Documentation

Full API reference: [docs/_build/html/index.html](docs/_build/html/index.html)

## License

GPLv3 — see [LICENSE](LICENSE).
