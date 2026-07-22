# Changelog

## [0.3.9] — 2026-07-22

### Fixed
- P1 — ProgressBar ahora es interactivo (click, command, bind("change"), variables)
- P2 — Dedup de eventos cambiado de clave-exacta a debounce temporal (50ms)
- P3 — `_eval_js` logea errores JS en stderr cuando `debug=True`
- P4 — `_sync()` protegido contra widgets destruidos o app no iniciada
- P5 — Variables `--progress-from`/`--progress-to` agregadas a los 7 temas

### Changed
- `Application(debug=True)` expone errores JS sin afectar producción

## [0.2.0] — 2026-07-21

### Added
- 36 widgets: Label, Button, Entry, CheckBox, RadioButton, ComboBox, Slider,
  ProgressBar, Frame, ListBox, ScrollBar, Text, SpinBox, Separator, Notebook,
  Canvas, Scale, MessageDialog, Knob, LEDDisplay, DataGrid, IndicatorLED,
  RadialGauge, ToggleSwitch, StatusBar, Tooltip, Spacer, ImageBox, IconLabel,
  RichText, TreeView, DropTarget, MenuBar, FileDialog, Menu, MenuItem
- Pack, grid, and place layout engines
- IFAZ Tactical Theme (dark, terminal-inspired CSS)
- JS bridge with deduplication for pywebview double-event delivery
- Menu system with nested submenus and keyboard shortcuts
- FileDialog (open, save, folder via native OS dialogs)
- MessageDialog (modal overlay via `insertAdjacentHTML`)
- Canvas with rectangle, line, oval, text, arc drawing primitives
- RadialGauge and Knob with mouse drag/wheel interaction
- LEDDisplay, IndicatorLED, ProgressBar for data visualization
- DataGrid with column sorting and row selection
- RichText editor with formatting toolbar
- TreeView with collapsible nodes
- Tooltip system
- DropTarget for drag-and-drop
- GTK stderr warning suppression during `run()`
- MIT license

### Changed
- Widgets refactored from monolithic `widgets.py` into subpackage `widgets/`
  with one file per category (`_controls.py`, `_display.py`, etc.)
- Legacy standalone files (`index.html`, `js/`, `css/`, `img/`) removed

### Infrastructure
- Sphinx documentation skeleton (`docs/conf.py`, `docs/index.rst`, `docs/api.rst`)
- `pyproject.toml` with setuptools build configuration
- `.gitignore` for Python/bytecode/cache/OS artifacts
