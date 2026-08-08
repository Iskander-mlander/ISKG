# Plan de mejoras ISKG

Ideas priorizadas para el roadmap. Se implementan **de una en una**, en el orden
marcado, para no mezclar cambios. Estado general:

- [x] Menú contextual por widget (clic derecho)
- [x] Señales globales / event bus
- [x] Widgets de datos (TimeSeriesGraph, Sparkline, LogViewer, Clock, DatePicker)
- [x] Atajos globales
- [x] Drag & drop nativo

## Menú contextual por widget (clic derecho)

Done. Ver `docs/api.rst` (`_menus`) y commit de la versión 0.3.80.

## Señales globales / event bus

`app.on("evento", cb)` + `app.emit(...)` — bus ligero con eventos integrados
`theme-changed`, `closing` y `widget-created`. Soporta decorador y `app.off`.

## Widgets de datos

- `TimeSeriesGraph`/`Sparkline`: gráficos SVG multi-serie con curvas Bézier
  suavizadas, `max_pts`, `y_min`/`y_max` y `append/replace/update/clear`.
- `LogViewer`: scrollable con colores por severidad, timestamps y autoscroll.
- `Clock` (tick en vivo) y `DatePicker` (popup de calendario con navegación).

## Calidad de vida

- Atajos globales (`app.bind("<Control-...>")` sin foco en widget, soporta
  decorador).
- Drag & drop nativo entre widgets con `draggable=True` + `bind("<<Drop>>")`.

---

Estado de pendientes:

- [x] Menú contextual por widget — 2026-08-08 (`set_menu`/`popup_menu`/`bind("contextmenu")`)
- [x] Señales globales / event bus — 2026-08-08 (`app.on`/`emit`/`off`)
- [x] TimeSeriesGraph / Sparkline — 2026-08-08
- [x] LogViewer — 2026-08-08
- [x] Calendar / DatePicker / Clock — 2026-08-08 (`DatePicker` + `Clock`)
- [x] Atajos globales — 2026-08-08 (`app.bind`)
- [x] Drag & drop nativo — 2026-08-08