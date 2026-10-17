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

## What's new in 0.4.17

* **Frames never cover their widgets again** — content-minimum
  propagation: every `Frame`/`Notebook`/`PanedWindow` computes the
  natural minimum of its children (pack sums, grid tracks, place
  bounds, chrome + header) and refuses to shrink below it, and the OS
  window itself gets a `min_size` from the whole tree
  (`Application(min_size=False)` opts out). `ScrolledFrame` keeps
  scrolling instead of propagating. Opt out per-widget with
  `fit=False`; explicit `width`/`height`/`min_width`/`min_height`
  always win.
* **Comfortable default metrics** (`iskg.metrics`): buttons 30px
  (sm 24 / lg 36 / tiny 18) at 12px font, entries 28px at 12px — the
  theme CSS and the minimum propagation share one source of truth.

## What's new in 0.4.16

* **Debug tools that actually work**: the bridge now keeps a 500-entry
  traffic trace — `app.trace()` shows every Python→JS eval, every
  JS→Python event, debounce drops and unhandled events (the classic
  "my click does nothing"), and `Application(debug=True)` echoes it to
  stderr. `app.dump_tree()` / `app.dump_tree_text()` print the whole
  widget tree as JSON or indented text; `app.get_widget(id)` looks one
  up.
* **`WidgetInspector` fixed** — it used to crash on `enable()`
  (`inject_js` did not exist) and swallowed picks without a handler.
  Now Alt+I / click-to-inspect shows a floating panel with the widget's
  class, id and full config, and emits `widget-picked`.
* **`fps_meter` fixed** — it registered a keyboard shortcut instead of
  a bridge handler, so it always returned 0. `Application.inject_js()`
  now exists (queue-safe before `run()`), unbreaking `SystemTray` and
  the picker toast. 910 tests pass.

## What's new in 0.4.12

* **`padx`/`pady` now accept tkinter-style tuples** in `pack()`, `grid()`
  and `Box`: `pady=(0, 8)` means *top 0, bottom 8*. Before, tuples were
  interpolated straight into CSS (`padding-top:(0, 8)px`), which the
  browser silently dropped — so every example using them lost its spacing.
  A single int still means "both sides", and `0` still emits nothing so
  class-level padding keeps working.
* `PadValue` is exported from `iskg` for annotating your own helpers.
* 869 tests pass (2 skipped).

## What's new in 0.4.11

* **Fixed blank/white window after the 2026-10 Arch update** (WebKitGTK
  2.54): ISKG now also sets `WEBKIT_DISABLE_DMABUF_RENDERER=1`, the
  documented workaround for GBM/dmabuf allocation failures on NVIDIA
  proprietary drivers. Set the variable yourself before launching to
  override.
* **`Application(icon=...)` with a missing file no longer hangs**: the path
  is validated up front — ISKG warns on stderr and starts without an icon
  instead of blocking forever in `run()`.
* Examples fixed (`async_task` icon, `data_widgets_demo` ListBox callback).
* `iskg themes` now lists the 16 runtime themes accepted by
  `app.set_theme()` instead of only the base CSS asset.
* Features section corrected: **71 widgets** (real names, real families)
  and **16 themes**. 858 tests pass.

## What's new in 0.4.10

* **macOS CI fix**: `tests/test_cli.py::test_run_non_python` no
  longer relies on `/etc/hostname` (which does not exist on macOS).
  854 tests pass on Linux, macOS, and Windows.

See [CHANGELOG.md](CHANGELOG.md) for the full history.

## Features

- **71 widgets** across 5 families:
  *inputs* (Button, Entry, CheckBox, RadioButton, ComboBox, Slider, Scale, SpinBox, ToggleSwitch, RangeSlider, SearchCtrl, ColorPicker, FontPicker, DirectoryPicker, ImagePicker, DatePicker, TimePicker, DateTimePicker, Calendar),
  *display* (Label, IconLabel, ImageBox, ProgressBar, ProgressCircle, RadialGauge, Knob, LEDDisplay, IndicatorLED, StatusBar, Spinner, Clock, Badge, Avatar, Carousel, RichText, Text, LogViewer, Tooltip, MarkdownViewer),
  *charts* (BarChart, PieChart, ScatterPlot, Heatmap, Sparkline, TimeSeriesGraph, Canvas, GraphicsView),
  *containers* (Frame, ScrolledFrame, Notebook, TabBar, PanedWindow, Box, HBox, VBox, Spacer, Separator, ToolBar, MdiArea, MdiSubWindow, Modal, DropTarget, FileBrowser, ScrollBar),
  *data & infra* (ListBox, DataGrid, TreeView, MenuBar, MessageDialog, PropertyGrid, CommandPalette).
- **16 built-in themes** (`app.set_theme("dracula")`, `iskg themes`), switchable at runtime — plus a custom theme registry.
- **`iskg` CLI** with `iskg new`, `iskg run`, `iskg check`, `iskg bundle --standalone|--exe`, and introspection commands (`iskg info`, `iskg widgets`, `iskg themes`).
- **Form validation** (`Form` + 8 validators: `Required`, `Range`, `Length`, `Pattern`, `Email`, `URL`, `Number`, `Custom`).
- **I18n / L10n**: `tr()` / `_()` with JSON or `.mo` catalogues, `format_number` / `format_date`, `use_language()` context manager.
- **Content-safe layout**: frames and the window propagate the natural minimum size of their content (`Widget._content_min_size()`, `fit=False` opt-out, `Application(min_size=False)` to disable) so widgets are never covered when resizing; shared defaults in `iskg.metrics`.
- **Debug tools**: bridge trace (`app.trace()` / `trace_clear()`), widget tree dumps (`app.dump_tree()` / `app.dump_tree_text()` / `Widget.dump()`), `qDebug` / `qInfo` / `qWarning` / `qCritical` print helpers, `WidgetInspector` (Alt+I, click-to-inspect panel + `widget-picked` event), `fps_meter`, `enable_hot_reload` for CSS.
- **Cross-platform**: Linux, Windows, macOS, BSD (same codebase). XDG paths on Linux, `~/Library/Application Support` on macOS, `%APPDATA%` on Windows.
- **Zero HTTP**: no server, no ports, no browser tabs — just a window.
- **JS bridge**: bidirectional Python ↔ JavaScript calls for real-time UI updates.
- **`.tooltip` on every widget**: set via property or `config()`.
- **`after()` timers**: cancellable timer objects with `.cancel()` and `.running`.
- **Window flags for overlays**: `Application(on_top=True, frameless=True, easy_drag=True, x=..., y=...)`, live `on_top()` toggle, real `geometry()` position, and `pywebview.api.resize(w, h)` / `pywebview.api.pause_drag()` for custom HTML resize grips on frameless windows.
- **7 embedded fonts** (SIL OFL): [Inter](https://rsms.me/inter/), [JetBrains Mono](https://www.jetbrains.com/lp/mono/), [Nunito](https://fonts.google.com/specimen/Nunito), [Manrope](https://manropefont.com/), [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk), [Fira Sans](https://fonts.google.com/specimen/Fira+Sans), [Playfair Display](https://fonts.google.com/specimen/Playfair+Display) — no CDN, todo embebido.

## Quick start

```bash
# desde PyPI
pip install iskg

# from GitHub Releases
pip install https://github.com/Iskander-mlander/ISKG/releases/download/v0.4.15/iskg-0.4.15-py3-none-any.whl
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
    row=0, column=0, columnspan=2, pady=4
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

Label(parent=root, text="Ready", anchor="center").grid(
    row=6, column=0, columnspan=2, pady=(0, 8)
)

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

#### Window opens blank/white on Linux

WebKitGTK ≥ 2.54 renders through GBM/dmabuf buffers; on drivers that cannot
allocate them (NVIDIA proprietary is the usual case) the window opens but
stays white and stderr shows `Failed to create GBM buffer ...`. ISKG sets
`WEBKIT_DISABLE_DMABUF_RENDERER=1` for you (with `setdefault`, so an
explicit value you export always wins):

```bash
WEBKIT_DISABLE_DMABUF_RENDERER=1 python app.py   # manual override
WEBKIT_DISABLE_DMABUF_RENDERER=0 python app.py   # force the dmabuf path back on
```

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
iskg --version           # 0.4.12
iskg info                # environment, Python, backends
iskg widgets             # list all public classes
iskg themes              # list runtime themes (set_theme names)
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
