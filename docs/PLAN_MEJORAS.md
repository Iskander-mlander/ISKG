# Plan de mejoras ISKG

Ideas priorizadas para el roadmap. Se implementan **de una en una**, en el orden
marcado, para no mezclar cambios. Estado general:

- [x] Menú contextual por widget (clic derecho)

## Menú contextual por widget (clic derecho)

Done.

## Señales globales / event bus

`app.on("evento", cb)` + `app.emit(...)`. Un bus ligero para notificar
`theme-changed`, `app.closing`, layout removido, etc. Refuerza las variables
vinculadas (`StringVar`...) ya existentes.

## Widgets de datos

- `TimeSeriesGraph`/`Sparkline`: mini-histórico RGB en canvas 2D (monitoreo).
- `LogViewer`: scrollable con colores por severidad y autoscroll.
- `Calendar`/`DatePicker` o `Clock` para HUDs.

## Calidad de vida

- Atajos globales (`Window.bind("<Control-...>")` sin foco en widget).
- Drag & drop nativo entre widgets con `<<Drop>>`.

---

Estado de pendientes (casilla + fecha):

- [x] Menú contextual por widget — 2026-08-08 (`set_menu`/`popup_menu`/`bind("contextmenu")`)
- [ ] Señales globales / event bus
- [ ] TimeSeriesGraph / Sparkline
- [ ] LogViewer
- [ ] Calendar / DatePicker / Clock
- [ ] Atajos globales
- [ ] Drag & drop nativo