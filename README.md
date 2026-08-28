<div align="center">
  <img src="https://raw.githubusercontent.com/Iskander-mlander/ISKG/main/iskg/examples/icon.png" width="80" alt="ISKG logo"/>
  <h1>ISKG</h1>
  <p><b>IFAZ Widget Toolkit</b> — Python GUI framework ligero</p>

  [![CI](https://img.shields.io/github/actions/workflow/status/Iskander-mlander/ISKG/ci.yml?branch=main&label=CI&logo=github)](https://github.com/Iskander-mlander/ISKG/actions)
  [![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python)](https://www.python.org)
  [![License](https://img.shields.io/github/license/Iskander-mlander/ISKG?color=green)](LICENSE)
  [![Release](https://img.shields.io/github/v/release/Iskander-mlander/ISKG?logo=github)](https://github.com/Iskander-mlander/ISKG/releases)
  [![Platform](https://img.shields.io/badge/platform-linux%20|%20windows%20|%20macos%20|%20bsd-lightgrey)](#)
</div>

---

**ISKG** renders native-looking widgets as HTML/CSS/JS inside a native window via [pywebview](https://github.com/r0x0r/pywebview).

No browser, no HTTP server — just a Python process and a lightweight WebView.

## What's new in 0.4.9

* **Pyright clean** across the whole package: 0 errors, 0 warnings.
* Type-safety fixes across `app.py`, `cli.py`, `i18n.py`,
  `_calendar.py`, `_charts2.py`, `_data.py`, `_extras.py`.
* `TreeView.remove(path)` renamed to `remove_node(path)` to
  avoid clashing with `Widget.remove(child)`.
* 854 tests still passing.

## What's new in 0.4.8

* **`iskg` CLI**: `iskg new`, `iskg run`, `iskg check`, `iskg bundle`,
  `iskg info/widgets/themes` — see [CLI](#cli).
* **Scaffolds**: `iskg new myapp --template tool|dashboard|form|viewer`.
* **Cross-platform packaging**: `pip install iskg` works on Linux, Windows,
  macOS, and BSD; the CLI uses XDG paths, `~/Library/Application Support`,
  or `%APPDATA%` as appropriate.
* 854 tests passing.

See [CHANGELOG.md](CHANGELOG.md) for the full history.

## Features

- **72 widgets** across 5 families: inputs (Button, Entry, ComboBox, Slider, SpinBox, ToggleSwitch, ColorPicker, FontPicker, DirectoryPicker, ImagePicker, SearchCtrl, DatePicker, Calendar, TimePicker, DateTimePicker), display (Label, ImageBox, IconLabel, RichText, IndicatorLED, LEDDisplay, Knob, RadialGauge, ProgressBar, ProgressCircle, Sparkline, TimeSeriesGraph, BarChart, PieChart, ScatterPlot, Heatmap, Clock, Badge, Avatar, Spinner, Toast, Carousel, MarkdownViewer, GraphicsView), containers (Frame, ScrolledFrame, PanedWindow, Notebook, TabBar, MdiArea, MdiSubWindow, Box, HBox, VBox, Spacer, Separator, ToolBar, PropertyGrid, CommandPalette, SystemTray, FileBrowser, Modal, DropTarget), data (ListBox, DataGrid, TreeView, Text, Canvas, LogViewer, Menu, MenuBar, MenuItem, StatusBar, Tooltip, RangeSlider), infra (UndoStack, FileDialog, MessageDialog, ScrollBar, Scale, Slider).
- **`iskg` CLI** with `iskg new`, `iskg run`, `iskg check`, `iskg bundle --standalone|--exe`, and introspection commands (`iskg info`, `iskg widgets`, `iskg themes`).
- **Form validation** (`Form` + 8 validators: `Required`, `Range`, `Length`, `Pattern`, `Email`, `URL`, `Number`, `Custom`).
- **I18n / L10n**: `tr()` / `_()` with JSON or `.mo` catalogues, `format_number` / `format_date`, `use_language()` context manager.
- **Debug tools**: `qDebug` / `qInfo` / `qWarning` / `qCritical` print helpers, `WidgetInspector` (Alt+I), `fps_meter`, `enable_hot_reload` for CSS.
- **Cross-platform**: Linux, Windows, macOS, BSD (same codebase). XDG paths on Linux, `~/Library/Application Support` on macOS, `%APPDATA%` on Windows.
- **Zero HTTP**: no server, no ports, no browser tabs — just a window.
- **JS bridge**: bidirectional Python ↔ JavaScript calls for real-time UI updates.
- **`.tooltip` on every widget**: set via property or `config()`.
- **`after()` timers**: cancellable timer objects with `.cancel()` and `.running`.
- **7 embedded fonts** (SIL OFL): [Inter](https://rsms.me/inter/), [JetBrains Mono](https://www.jetbrains.com/lp/mono/), [Nunito](https://fonts.google.com/specimen/Nunito), [Manrope](https://manropefont.com/), [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk), [Fira Sans](https://fonts.google.com/specimen/Fira+Sans), [Playfair Display](https://fonts.google.com/specimen/Playfair+Display) — no CDN, todo embebido.

## Quick start

```bash
# desde PyPI
pip install iskg

# from GitHub Releases
pip install https://github.com/Iskander-mlander/ISKG/releases/download/v0.4.9/iskg-0.4.9-py3-none-any.whl
```

```python
from iskg import (
    Application,
    Button,
    Entry,
    Label,
    Frame,
    Slider,
    ComboBox,
    ProgressBar,
    ToggleSwitch,
)

app = Application(title="ISKG Quick Start", width=560, height=420)

# Root frame with a stretchable column 0
root = Frame(parent=None)
root.grid_columnconfigure(0, weight=1)

Label(parent=root, text="ISKG QUICK START", anchor="center", font="bold 16px").grid(
    row=0, column=0, columnspan=2, pady=(8, 4)
)

# Greet: Entry in column 0, Button in column 1
name = Entry(parent=root, text="world")
name.grid(row=1, column=0, sticky="we", padx=8)

greeting = Label(parent=root, text="Hello, world!")
greeting.grid(row=2, column=0, sticky="w", padx=8)


def on_greet():
    greeting.config(text=f"Hello, {name.text or 'world'}!")


Button(parent=root, text="Greet", command=on_greet).grid(row=1, column=1, padx=8)

# Slider drives the ProgressBar
slider = Slider(parent=root, from_=0, to=100, value=30)
slider.grid(row=3, column=0, sticky="we", padx=8)

progress = ProgressBar(parent=root, max_=100, value=30)
progress.grid(row=4, column=0, sticky="we", padx=8)


def on_slider_change(_data):
    progress.value = slider.value


slider.bind("change", on_slider_change)

# Theme picker + a toggle
combo = ComboBox(
    parent=root,
    values=["ifaz", "desert", "cyberdusk", "night", "warm", "cold", "light"],
    command=lambda _d: app.set_theme(combo.value),
)
combo.grid(row=5, column=0, sticky="we", padx=8)

ToggleSwitch(parent=root, text="Extra").grid(row=5, column=1, padx=8)

Label(parent=root, text="Ready", anchor="center").grid(row=6, column=0, columnspan=2, pady=8)

app.add(root)
app.run()
```

## Installation

```bash
pip install iskg          # desde PyPI (Python 3.10+)
```

### Platform-specific dependencies (pywebview backends)

ISKG uses `pywebview` which delegates to a native WebView. You need:

**Linux (any distro)** — install WebKit2GTK + GTK3 + GObject Introspection:

```bash
# Arch / Manjaro
sudo pacman -S gtk3 webkit2gtk-4.1 python-gobject

# Debian / Ubuntu
sudo apt install python3-gi gir1.2-webkit2-4.1

# Fedora
sudo dnf install gtk3 webkit2gtk4.1 python3-gobject

# openSUSE
sudo zypper install gtk3 libwebkit2gtk-4_1-0 python3-gobject
```

**Windows** — `pywebview` ships with a bundled Edge WebView2 runtime. No additional
system dependencies required. **Python 3.10+** (32 or 64 bit). If Edge WebView2 is
not installed (older Windows 10 builds), download it from
[microsoft.com](https://developer.microsoft.com/microsoft-edge/webview2/).

**macOS** — uses the system `WKWebView` (no install needed). **Python 3.10+**.
`pyobjc` is installed automatically by `pywebview`.

**BSD** — same as Linux, but install via your package manager
(`webkit2-gtk3`, `gtk3`, `py3-gobject3` on FreeBSD).

### Arch Linux — PEP 668

Arch's Python is *externally-managed*, so a bare `pip install iskg` fails. Pick one:

```bash
# 1. Virtualenv (recommended)
python -m venv .venv && .venv/bin/pip install iskg

# 2. pipx (cleanest for a CLI tool)
pipx install iskg

# 3. System-wide, at your own risk
pip install --break-system-packages iskg
```

### From source

```bash
git clone https://github.com/Iskander-mlander/ISKG.git
cd ISKG
pip install -e .
```

## CLI

Once installed, `iskg` is on your `PATH`:

```bash
iskg --version           # 0.4.9
iskg info                # environment, Python, backends
iskg widgets             # list all public classes
iskg themes              # list bundled CSS themes
iskg check app.py        # syntax-check a script
iskg run app.py          # run a script
iskg new mytool          # scaffold a "tool" project
iskg new myapp --template dashboard
iskg new myform --template form
iskg new myview --template viewer
iskg bundle app.py --standalone   # produce a self-contained .html
iskg bundle app.py --exe          # print a PyInstaller onefile command
```

### Scaffold a new project

```bash
$ iskg new mytool
creating /home/you/mytool from template 'tool'…
  + app.py
  + README.md
  + requirements.txt
  + assets/README.md
  + themes/README.md

Done. Next steps:
  cd mytool
  iskg run app.py
```

Each template includes a working `app.py`, README, and the standard
`assets/` + `themes/` directories. Replace the stub logic with your own.

### Bundle for distribution

```bash
# Single HTML file (drop into a USB stick, open in any browser)
iskg bundle app.py --standalone

# Standalone executable
pip install pyinstaller
iskg bundle app.py --exe
# then run the printed pyinstaller command
```

## Documentation

Full API reference: [github-pages](https://iskander-mlander.github.io/ISKG/)

## License

GPLv3 — see [LICENSE](LICENSE).
