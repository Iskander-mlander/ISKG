# Changelog

## [0.3.70] — 2026-08-07

### Fixed
- Diálogo nativo de carpeta/archivo (GTK) congelaba la app y crasheaba WebKit:
  pywebview despacha las llamadas del bridge JS en un hilo worker, pero ISKG
  ejecutaba `dialog.run()` en ese hilo. Nuevo `Application._run_gtk_modal()`, que
  ejecuta el diálogo en el hilo principal vía `GLib.idle_add` + `Event` (mismo
  patrón que el `create_file_dialog` interno de pywebview). Aplicado a
  `file_dialog`, `color_dialog` y `font_dialog`.
- Pulsar Cancelar en el diálogo GTK abría un segundo diálogo (el fallback de
  pywebview) porque `None` se confundía con "GTK no disponible": `_gtk_file_dialog`
  devuelve ahora el sentinel `_GTK_UNAVAILABLE` cuando no importa GTK, y
  `file_dialog` sólo cae al diálogo de pywebview en ese caso.
- Botones con altura inconsistente: `Button(size="sm"|"lg")` generaba clases CSS
  sin reglas. Ahora `.iskg-btn` usa `height` fija por tamaño (26/22/30/18px) con
  el texto centrado y `padding` horizontal variable, de modo que todos los botones
  de un mismo tamaño comparten altura exacta y el ancho sólo sigue al texto.
- Dropdown de `ComboBox` recortado sin overlay: ahora en apertura se renderiza con
  `position:fixed` (+ `width`/`left`/`top` calculados con `getBoundingClientRect`),
  escapando el `overflow:hidden` y contextos de apilamiento de cualquier ancestro.

## [0.3.69] — 2026-08-07

### Fixed
- 7 tests preexistentes que fallaban desde v0.3.62 (la suite pasa ahora 604/604):
  - `Widget`: validación de tipos en `config()`/`__init__` (`visible`→bool, `text`→str,
    `disabled`/`hidden`→bool): se lanza `TypeError` ante tipos inválidos. `None` se
    permite siempre; `width`/`height` no se validan estrictamente por aceptar CSS
    ("95%", "10px").
  - `_render_style_update_js()`: cache del último CSS → segunda llamada con el mismo
    estilo devuelve "", sólo reenvía al cambiar.
  - `FileDialog.open_file/save_file/open_folder`: ahora reenvían `title` a
    `Application.file_dialog(..., title=...)`, que a su vez lo usa en el diálogo GTK.
  - `Application.get_clipboard/set_clipboard`: importan `pyperclip` vía
    `importlib.import_module` para soportar mocking y fallar a `""` ante ImportError.

## [0.3.68] — 2026-08-07

### Fixed
- Ventana completamente blanca (sin contenido) en Linux/webkit2gtk por un fallo del
  camino de compositing acelerado. `Application.run()` ahora fuerza
  `WEBKIT_DISABLE_COMPOSITING_MODE=1` (con `setdefault`, respetando override
  del usuario) antes de arrancar el loop GTK, de modo que la UI es siempre visible.
- Fallback de color de fondo en `template.py` (`body`/`#iskg-root`): si una
  variable CSS de tema queda sin definir, se usa un fondo oscuro en vez de blanco.

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
