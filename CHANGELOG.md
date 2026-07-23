# Changelog

## [0.3.67] — 2026-07-24

### Added
- Canvas: `create_polygon(*points, **kwargs)` — polígonos rellenos con contorno
- Canvas: `create_image(x, y, data, **kwargs)` — blit de tiles PNG desde bytes
- Canvas: `<<Resize>>` event via `ResizeObserver` + bridge — notifica `{width, height}`
- Documentación de API regenerada para nuevos métodos de Canvas

## [0.3.62] — 2026-07-23

### Added
- ARIA attributes (`role`, `aria-*`) en todos los widgets — accesibilidad para screen-readers (#M4)
- Docstrings en ~140 métodos públicos de la API (#M5)
- Test de integración ScrolledFrame + PanedWindow + grid mixto (#F4)

### Fixed
- SyntaxError en `ProgressBar` por `"""` huérfano en `_display.py`
- `aria-disabled="true"` perdido en CheckBox, RadioButton, Slider, SpinBox, ToggleSwitch
- `_render_attrs()` no se emitía en ProgressBar, StatusBar, ScrollBar, ListBox, DataGrid, TreeView, DropTarget, MenuBar, ComboBox, Slider, SpinBox, Scale, Notebook, RichText
- Separator, Entry, Text, RichText sin `_ARIA_ROLE`

### Changed
- Widgets reordenados en demo (gauges, botones 2-col)

## [0.3.11] — 2026-07-22

### Added
- ImageBox: soporte para `command` callback y click (cursor:pointer, `iskg_bridge_event`)
- ImageBox: `width` y `height` aceptan `str` (ej. `"100%"`) además de `int`

### Changed
- ImageBox: ancho/alto renderizado con unidad `px` solo si es `int`

## [0.3.10] — 2026-07-22

### Added
- 8 nuevos temas: infinity (neón), cyberdusk (azul), dracula, nord, gruvbox, monokai, catppuccin, light
- 7 fuentes SIL OFL embebidas (Inter, JetBrains Mono, Nunito, Manrope, Space Grotesk, Fira Sans, Playfair Display) — sin CDN
- `AGENTS.md` con workflow checklist para sesiones futuras
- Nuevas variables CSS: `--font-sans`, `--font-rounded`, `--font-geometric`, `--font-display-alt`, `--font-humanist`, `--font-serif`

### Changed
- Reemplazados 5 temas antiguos (cold, warm, night, ocean) por 8 nuevos
- Descripción del proyecto: eliminada mención "táctico-militar"
- Fuentes CDN (Share Tech Mono, Orbitron) reemplazadas por fuentes embebidas
- Documentación de API actualizada con módulo fonts y lista de temas

## [0.3.9] — 2026-07-22

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
