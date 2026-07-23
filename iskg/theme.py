IFAZ_CSS = r"""
:root {
  --bg-primary: #070b10;
  --bg-panel: #0c111a;
  --bg-panel-alt: #111822;
  --bg-panel-hi: #16202e;
  --border: #1a2636;
  --border-light: #28364a;
  --green: #4ade80;
  --green-dim: #0f2e1a;
  --amber: #f59e0b;
  --amber-dim: #2e2008;
  --red: #ef4444;
  --red-dim: #2e0e0e;
  --cyan: #22d3ee;
  --cyan-dim: #0a2030;
  --text: #c8d6e5;
  --text-dim: #4a5a6a;
  --text-green: #7ec850;
  --glow-green: 0 0 6px rgba(74, 222, 128, 0.25);
  --glow-amber: 0 0 6px rgba(245, 158, 11, 0.25);
  --glow-red: 0 0 6px rgba(239, 68, 68, 0.25);
  --glow-cyan: 0 0 6px rgba(34, 211, 238, 0.2);
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;
  --font-display: 'Inter', 'Segoe UI', Tahoma, sans-serif;
  --font-sans: 'Inter', 'Segoe UI', Tahoma, sans-serif;
  --font-rounded: 'Nunito', sans-serif;
  --font-geometric: 'Manrope', sans-serif;
  --font-display-alt: 'Space Grotesk', sans-serif;
  --font-humanist: 'Fira Sans', sans-serif;
  --font-serif: 'Playfair Display', serif;
  --radius: 2px;
  --transition-speed: 0.12s;
}

* { margin:0; padding:0; box-sizing:border-box; }
:focus-visible { outline:1px solid var(--green); outline-offset:1px; }

html, body {
  width:100%; height:100%; overflow:hidden;
  background:var(--bg-primary); color:var(--text);
  font-family:var(--font-mono); font-size:12px;
  user-select:none; cursor:default;
}

#iskg-root {
  width:100vw; height:100vh;
  display:flex; flex-direction:column;
  background:var(--bg-primary);
  padding:6px; gap:4px;
}

#iskg-root > .iskg-frame { flex:1; }

/* ===== BUTTON ===== */
.iskg-btn {
  font-family:var(--font-mono);
  font-size:10px; letter-spacing:1px;
  padding:5px 14px;
  background:var(--bg-panel-alt);
  border:1px solid var(--border-light);
  color:var(--text); border-radius:var(--radius);
  cursor:pointer; text-transform:uppercase;
  transition:all var(--transition-speed); white-space:nowrap;
  line-height:1.2;
}
.iskg-btn:hover {
  background:var(--bg-panel-hi);
  border-color:var(--green); color:var(--green);
  box-shadow:var(--glow-green);
}
.iskg-btn:focus-visible {
  border-color:var(--cyan);
  box-shadow:var(--glow-cyan);
}
.iskg-btn:active { transform:scale(0.95); }
.iskg-btn:disabled {
  opacity:0.35; cursor:default; pointer-events:none;
}
.iskg-btn.active {
  background:var(--green-dim);
  border-color:var(--green); color:var(--green);
  box-shadow:var(--glow-green);
}
.iskg-btn.danger { border-color:var(--red-dim); color:var(--red); }
.iskg-btn.danger:hover { background:var(--red-dim); border-color:var(--red); box-shadow:var(--glow-red); }
.iskg-btn.caution { border-color:var(--amber-dim); color:var(--amber); }
.iskg-btn.caution:hover { background:var(--amber-dim); border-color:var(--amber); box-shadow:var(--glow-amber); }
.iskg-btn.small { padding:3px 10px; font-size:9px; }
.iskg-btn.tiny { padding:2px 6px; font-size:8px; }

.iskg-btn.pulsed {
  animation: iskg-pulsedBtn 2s infinite;
}
@keyframes iskg-pulsedBtn {
  0%,100% { border-color:var(--border-light); }
  50% { border-color:var(--cyan); box-shadow:0 0 5px rgba(34,211,238,0.25); }
}

/* ===== LABEL ===== */
.iskg-label {
  font-family:var(--font-mono);
  font-size:11px; color:var(--text);
  line-height:1.5;
  padding:2px 2px;
}
.iskg-label.cyan { color:var(--cyan); }
.iskg-label.green { color:var(--green); }
.iskg-label.amber { color:var(--amber); }
.iskg-label.red { color:var(--red); }
.iskg-label.dim { color:var(--text-dim); }
.iskg-label.heading {
  font-family:var(--font-display);
  font-size:10px; letter-spacing:2px;
  color:var(--text-dim);
  text-transform:uppercase;
}

/* ===== ENTRY ===== */
.iskg-entry {
  font-family:var(--font-mono);
  font-size:11px; color:var(--cyan);
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:4px 8px;
  outline:none;
  transition:border-color var(--transition-speed);
  caret-color:var(--cyan);
  width:150px;
}
.iskg-entry:hover { border-color:var(--border-light); }
.iskg-entry:focus {
  border-color:var(--cyan);
  box-shadow:var(--glow-cyan);
}
.iskg-entry:disabled {
  opacity:0.35; cursor:default;
}

/* ===== CHECKBOX / RADIO ===== */
.iskg-check-wrap, .iskg-radio-wrap {
  display:inline-flex; align-items:center; gap:6px;
  cursor:pointer;
  font-family:var(--font-mono); font-size:11px; color:var(--text);
  padding:2px 6px; margin:1px 0;
}
.iskg-check-wrap.disabled, .iskg-radio-wrap.disabled {
  opacity:0.35; cursor:default; pointer-events:none;
}
.iskg-check, .iskg-radio {
  width:16px; height:16px; flex-shrink:0;
  background:var(--bg-panel-alt);
  border:1px solid var(--border-light);
  border-radius:2px;
  position:relative;
  transition:all var(--transition-speed);
}
.iskg-check-wrap:hover .iskg-check,
.iskg-radio-wrap:hover .iskg-radio {
  border-color:var(--green);
  box-shadow:var(--glow-green);
}
.iskg-radio { border-radius:50%; }
.iskg-check.checked {
  background:var(--green-dim);
  border-color:var(--green);
}
.iskg-check.checked::after {
  content:'✓'; position:absolute;
  top:0px; left:3px;
  font-size:12px; color:var(--green);
}
.iskg-radio.checked {
  background:var(--green-dim);
  border-color:var(--green);
}
.iskg-radio.checked::after {
  content:''; position:absolute;
  top:3px; left:3px;
  width:8px; height:8px;
  background:var(--green);
  border-radius:50%;
  box-shadow:var(--glow-green);
}

/* ===== COMBOBOX ===== */
.iskg-cb-wrap {
  position:relative; display:inline-block;
  font-size:11px; font-family:var(--font-mono);
  vertical-align:top;
  width:140px;
}
.iskg-cb-display {
  display:flex; align-items:center; justify-content:space-between;
  gap:4px;
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:4px 8px;
  cursor:pointer; color:var(--text);
  transition:border-color var(--transition-speed);
  user-select:none;
}
.iskg-cb-display:hover {
  border-color:var(--border-light);
}
.iskg-cb-open .iskg-cb-display {
  border-color:var(--cyan);
  box-shadow:var(--glow-cyan);
}
.iskg-cb-arrow {
  color:var(--text-dim); font-size:8px;
  transition:transform 0.15s;
}
.iskg-cb-open .iskg-cb-arrow {
  transform:rotate(180deg); color:var(--cyan);
}
.iskg-cb-drop {
  position:absolute; top:100%; left:0; right:0;
  z-index:1000;
  background:var(--bg-panel);
  border:1px solid var(--border-light);
  border-top:none;
  border-radius:0 0 var(--radius) var(--radius);
  max-height:180px; overflow-y:auto;
  box-shadow:0 4px 16px rgba(0,0,0,0.5);
}
.iskg-cb-item {
  padding:4px 10px; cursor:pointer;
  color:var(--text); font-size:11px;
  transition:background var(--transition-speed);
}
.iskg-cb-item:hover {
  background:var(--bg-panel-hi);
  color:var(--green);
}
.iskg-cb-sel {
  background:var(--green-dim);
  color:var(--green);
  border-left:2px solid var(--green);
}
.iskg-cb-input {
  font-family:var(--font-mono);
  font-size:11px; color:var(--cyan);
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:4px 8px;
  outline:none;
  caret-color:var(--cyan);
}
.iskg-cb-input:focus {
  border-color:var(--cyan);
  box-shadow:var(--glow-cyan);
}

/* ===== SLIDER ===== */
.iskg-slider-wrap {
  display:flex; align-items:center; gap:8px;
}
.iskg-slider {
  -webkit-appearance:none; appearance:none;
  flex:1; height:4px;
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:3px; outline:none;
}
.iskg-slider::-webkit-slider-thumb {
  -webkit-appearance:none; width:14px; height:14px;
  background:var(--cyan); border-radius:50%;
  cursor:pointer; box-shadow:var(--glow-cyan);
}
.iskg-slider::-moz-range-thumb {
  width:14px; height:14px;
  background:var(--cyan); border:none; border-radius:50%;
  cursor:pointer;
}
.iskg-slider:focus { border-color:var(--cyan); }
.iskg-slider:hover { border-color:var(--green); }
.iskg-slider:hover::-webkit-slider-thumb { box-shadow:0 0 10px rgba(34,211,238,0.4); }
.iskg-slider:disabled { opacity:0.35; }
.iskg-slider:disabled::-webkit-slider-thumb { cursor:default; }

.iskg-slider-vert {
  -webkit-appearance:none; appearance:none;
  transform:rotate(-90deg);
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:3px; outline:none;
}
.iskg-slider-vert-track {
  display:flex; align-items:center; justify-content:center;
  overflow:hidden; position:relative;
}
.iskg-slider-vert::-webkit-slider-thumb {
  -webkit-appearance:none; width:14px; height:14px;
  background:var(--cyan); border-radius:50%;
  cursor:pointer; box-shadow:var(--glow-cyan);
}
.iskg-slider-vert::-moz-range-thumb {
  width:14px; height:14px;
  background:var(--cyan); border:none; border-radius:50%;
  cursor:pointer;
}
.iskg-slider-vert:hover { border-color:var(--green); }

.iskg-slider-val {
  font-size:10px; color:var(--cyan);
  min-width:30px; text-align:right;
}
.iskg-slider-val-center {
  font-size:10px; color:var(--cyan);
  text-align:center;
}

/* ===== PROGRESS BAR ===== */
.iskg-progress-wrap {
  width:100%; height:16px;
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:8px;
  overflow:hidden; position:relative;
}
.iskg-progress-fill {
  height:100%;
  background:linear-gradient(90deg, var(--progress-from, var(--green-dim)), var(--progress-to, var(--amber-dim)));
  transition:width 0.3s;
}
.iskg-progress-text {
  position:absolute;
  top:0; left:0; right:0;
  text-align:center;
  font-size:10px; line-height:16px;
  color:var(--text);
}

/* ===== FRAME ===== */
.iskg-frame {
  background:var(--bg-panel);
  border:1px solid var(--border);
  border-radius:3px;
  padding:6px;
  position:relative;
  box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
}
.iskg-frame:hover {
  border-color: var(--border-light);
}
.iskg-frame::before {
  content:'';
  position:absolute;
  top:-1px; left:20px; right:20px;
  height:1px;
  background: linear-gradient(90deg, transparent, rgba(74,222,128,0.15), transparent);
  animation: iskg-panelGlide 4s ease-in-out infinite;
  pointer-events:none;
}
@keyframes iskg-panelGlide {
  0%, 100% { opacity:0.3; transform:scaleX(0.8); }
  50% { opacity:1; transform:scaleX(1); }
}

.iskg-frame-header {
  font-family:var(--font-display);
  font-size:10px; letter-spacing:2px;
  color:var(--text-dim);
  border-bottom:1px solid var(--border);
  padding-bottom:3px; margin-bottom:6px;
  text-transform:uppercase;
  display:flex; align-items:center; gap:5px;
}
.iskg-frame-header .hdr-dot {
  display:inline-block;
  width:5px; height:5px;
  background:var(--green);
  box-shadow:var(--glow-green);
  border-radius:50%;
  animation: iskg-dotPulse 2s ease-in-out infinite;
}
@keyframes iskg-dotPulse {
  0%,100% { opacity:0.4; transform:scale(0.8); }
  50% { opacity:1; transform:scale(1.2); }
}

/* ===== LISTBOX ===== */
.iskg-listbox {
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:var(--radius);
  overflow-y:auto;
  font-family:var(--font-mono); font-size:11px;
  min-height:60px;
}
.iskg-listbox-item {
  padding:3px 8px;
  cursor:pointer;
  transition:background var(--transition-speed);
}
.iskg-listbox-item:hover {
  background:var(--bg-panel-hi);
  color:var(--green);
}
.iskg-listbox-item.selected {
  background:var(--green-dim);
  color:var(--green);
  border-left:2px solid var(--green);
}

/* ===== TEXT/MULTILINE ===== */
.iskg-text {
  font-family:var(--font-mono);
  font-size:11px; color:var(--cyan);
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:4px 8px;
  outline:none; resize:none;
  caret-color:var(--cyan);
  line-height:1.5;
  min-height:150px;
}
.iskg-text:hover { border-color:var(--border-light); }
.iskg-text:focus {
  border-color:var(--cyan);
  box-shadow:var(--glow-cyan);
}
.iskg-text:disabled { opacity:0.35; }

/* ===== SPINBOX ===== */
.iskg-spinbox-wrap {
  display:inline-flex; align-items:stretch;
}
.iskg-spinbox {
  font-family:var(--font-mono);
  font-size:11px; color:var(--cyan);
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-right:none;
  padding:4px 8px;
  width:60px; text-align:center;
  outline:none;
}
.iskg-spinbox:focus { border-color:var(--cyan); }
.iskg-spinbox:disabled { opacity:0.35; }
.iskg-spinbox-btns {
  display:flex; flex-direction:column;
}
.iskg-spinup, .iskg-spindown {
  flex:1; min-width:22px; min-height:12px;
  font-family:var(--font-mono);
  font-size:8px; color:var(--cyan);
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  line-height:1;
  padding:1px 4px;
}
.iskg-spinup { border-bottom:none; }
.iskg-spinup:hover, .iskg-spindown:hover {
  background:var(--bg-panel-hi);
  border-color:var(--cyan);
}

/* ===== SEPARATOR ===== */
.iskg-hsep {
  height:0;
  border:none;
  border-top:1px solid var(--border);
  margin:6px 0;
}
.iskg-vsep {
  width:0;
  border:none;
  border-left:1px solid var(--border);
  margin:0 6px;
}

/* ===== NOTEBOOK / TABS ===== */
.iskg-scrollframe {
  display:flex; flex-direction:column; flex:1; min-height:0;
}
.iskg-panedwindow {
  display:flex; min-height:0; min-width:0;
}
.iskg-sash {
  background:var(--border); flex-shrink:0; position:relative;
  transition:background var(--transition-speed);
  z-index:10;
}
.iskg-sash:hover {
  background:var(--green-dim);
}
.iskg-sash::after {
  content:''; position:absolute;
  top:50%; left:50%; transform:translate(-50%,-50%);
  width:12px; height:12px;
  background:radial-gradient(circle,var(--text-dim) 1px,transparent 1px);
  background-size:4px 4px;
  opacity:0.4;
}
.iskg-notebook {
  display:flex; flex-direction:column;
  flex:1; min-height:0;
}
.iskg-tabbar {
  display:flex; gap:2px;
  border-bottom:1px solid var(--border);
  flex-shrink:0;
}
.iskg-tab {
  font-family:var(--font-mono);
  font-size:10px; letter-spacing:1px;
  padding:6px 12px;
  background:var(--bg-panel);
  border:1px solid var(--border);
  border-bottom:none;
  color:var(--text-dim);
  cursor:pointer;
  border-radius:2px 2px 0 0;
  transition:all var(--transition-speed);
}
.iskg-tab:hover { color:var(--text); background:var(--bg-panel-alt); }
.iskg-tab:focus-visible { outline:1px solid var(--cyan); outline-offset:-1px; }
.iskg-tab.active {
  background:var(--bg-panel-alt);
  color:var(--green);
  border-color:var(--border-light);
}
.iskg-tabpage {
  flex:1;
  border:1px solid var(--border-light);
  border-top:none;
  padding:6px;
  background:var(--bg-panel-alt);
  min-height:0;
}

/* ===== SCROLLBAR (native) ===== */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:var(--bg-primary); }
::-webkit-scrollbar-thumb { background:var(--border-light); border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:var(--text-dim); }

/* ===== SCROLLBAR (iskg widget) ===== */
.iskg-scrollbar {
  position:relative;
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:2px;
  transition:border-color var(--transition-speed);
}
.iskg-scrollbar:hover { border-color:var(--green); }
.iskg-scrollbar-vert { width:10px; }
.iskg-scrollbar-horiz { height:10px; }
.iskg-scrollbar-thumb {
  position:absolute;
  background:var(--border-light);
  border-radius:2px;
  transition:background var(--transition-speed);
}
.iskg-scrollbar-thumb:hover { background:var(--text-dim); }
.iskg-scrollbar:disabled { opacity:0.35; }
.iskg-scrollbar-vert .iskg-scrollbar-thumb { left:1px; right:1px; }
.iskg-scrollbar-horiz .iskg-scrollbar-thumb { top:1px; bottom:1px; }

/* ===== CANVAS ===== */
.iskg-canvas {
  border:1px solid var(--border);
  background:var(--bg-primary);
}

/* ===== SCALE ===== */
.iskg-scale-wrap {
  display:flex; flex-direction:column; gap:2px;
}
.iskg-scale-labels {
  display:flex; justify-content:space-between;
  font-size:9px; color:var(--text-dim);
}

/* ===== MESSAGE BOX OVERLAY ===== */
.iskg-msgbox-overlay {
  position:fixed; top:0; left:0;
  width:100%; height:100%;
  background:rgba(0,0,0,0.7);
  display:none; align-items:center; justify-content:center;
  z-index:10000;
}
.iskg-msgbox-overlay.active {
  display:flex;
}
.iskg-msgbox {
  background:var(--bg-panel);
  border:1px solid var(--border-light);
  border-radius:3px;
  padding:16px;
  min-width:300px; max-width:450px;
  box-shadow:0 0 30px rgba(0,0,0,0.5);
}
.iskg-msgbox-title {
  font-family:var(--font-display);
  font-size:10px; letter-spacing:2px;
  color:var(--green);
  text-transform:uppercase;
  margin-bottom:8px;
}
.iskg-msgbox-text {
  font-size:11px; color:var(--text);
  margin-bottom:12px; line-height:1.5;
  white-space:pre-wrap;
}
.iskg-msgbox-btns {
  display:flex; gap:6px; justify-content:flex-end;
}

/* ===== UTILITY ===== */
.iskg-cyan { color:var(--cyan); }
.iskg-green { color:var(--green); }
.iskg-amber { color:var(--amber); }
.iskg-red { color:var(--red); }
.iskg-dim { color:var(--text-dim); }

.iskg-pad-xxs { padding:2px; }
.iskg-pad-xs { padding:4px; }
.iskg-pad-sm { padding:8px; }
.iskg-pad-md { padding:12px; }

.iskg-gap-xs { gap:2px; }
.iskg-gap-sm { gap:4px; }
.iskg-gap-md { gap:8px; }

/* ===== LAYOUT: PACK (flexbox) ===== */
.iskg-pack-top { display:flex; flex-direction:column; }
.iskg-pack-bottom { display:flex; flex-direction:column-reverse; }
.iskg-pack-left { display:flex; flex-direction:row; }
.iskg-pack-right { display:flex; flex-direction:row-reverse; }

.iskg-fill-both { flex:1; min-height:0; min-width:0; }
.iskg-fill-x { width:100%; }
.iskg-fill-y { height:100%; }
.iskg-expand { flex:1; min-height:0; min-width:0; }

/* ===== LAYOUT: GRID ===== */
.iskg-grid {
  display:grid;
  gap:3px;
}

/* ===== KNOB ===== */
.iskg-knob-wrap {
  display:flex; flex-direction:column; align-items:center; gap:4px;
}
.iskg-knob-canvas { cursor:pointer; border-radius:50%; transition:box-shadow 0.25s; }
.iskg-knob-canvas:hover { box-shadow:0 0 10px 3px var(--cyan); }
.iskg-knob-val {
  font-size:10px; color:var(--cyan); text-align:center;
}

/* ===== LED DISPLAY ===== */
.iskg-led-wrap {
  display:inline-flex; flex-direction:column; gap:2px;
}
.iskg-led-label {
  font-size:8px; letter-spacing:2px; text-transform:uppercase;
  color:var(--text-dim); text-align:center;
}
.iskg-led-digits {
  background:var(--bg-panel-alt); border:1px solid var(--border);
  border-radius:2px; padding:4px 8px;
  font-family:'Share Tech Mono', monospace;
  font-weight:bold; letter-spacing:3px;
  text-shadow:0 0 8px currentColor;
}
.iskg-led-green { color:var(--green); }
.iskg-led-red { color:var(--red); }
.iskg-led-amber { color:var(--amber); }
.iskg-led-cyan { color:var(--cyan); }

/* ===== DATA GRID ===== */
.iskg-datagrid {
  display:flex; flex-direction:column;
  border:1px solid var(--border);
  background:var(--bg-panel-alt);
  overflow:auto;
}
.iskg-datagrid table {
  width:100%; border-collapse:collapse;
  font-size:11px; font-family:var(--font-mono);
}
.iskg-datagrid th {
  background:var(--bg-panel-hi); color:var(--cyan);
  font-weight:normal; text-align:left;
  padding:4px 8px; border-bottom:1px solid var(--border);
  cursor:pointer; user-select:none; white-space:nowrap;
  position:sticky; top:0; z-index:1;
}
.iskg-datagrid th:hover { color:var(--green); }
.iskg-datagrid th .arrow { margin-left:4px; font-size:8px; }
.iskg-datagrid td {
  padding:3px 8px; border-bottom:1px solid var(--border);
  white-space:nowrap;
}
.iskg-datagrid tr:nth-child(even) td { background:var(--bg-panel-alt); }
.iskg-datagrid tr:nth-child(odd) td { background:var(--bg-primary); }
.iskg-datagrid tr:hover td { background:var(--bg-panel-hi); }
.iskg-datagrid tr.selected td { background:var(--cyan-dim); color:var(--cyan); }

/* ===== INDICATOR LED ===== */
.iskg-indicator {
  display:inline-flex; align-items:center; gap:6px;
}
.iskg-indicator-dot {
  border-radius:50%; flex-shrink:0;
  transition:all var(--transition-speed);
}
.iskg-indicator-on { opacity:1; }
.iskg-indicator-off { opacity:0.25; }
.iskg-indicator-label { font-size:10px; color:var(--text-dim); }

/* ===== RADIAL GAUGE ===== */
.iskg-gauge-wrap {
  display:flex; flex-direction:column; align-items:center; gap:2px;
}
.iskg-gauge-canvas { display:block; }
.iskg-gauge-label {
  font-size:8px; letter-spacing:1px;
  color:var(--text-dim); text-align:center;
}

/* ===== TOGGLE SWITCH ===== */
.iskg-toggle-wrap {
  display:inline-flex; align-items:center; gap:8px;
  cursor:pointer; user-select:none;
}
.iskg-toggle-track {
  width:32px; height:16px;
  background:var(--bg-panel-hi); border:1px solid var(--border);
  border-radius:8px; position:relative;
  transition:all var(--transition-speed);
}
.iskg-toggle-track.checked {
  background:var(--green-dim); border-color:var(--green);
}
.iskg-toggle-knob {
  position:absolute; top:1px; left:1px;
  width:12px; height:12px; border-radius:50%;
  background:var(--text-dim);
  transition:all var(--transition-speed);
}
.iskg-toggle-track.checked .iskg-toggle-knob {
  left:17px; background:var(--green);
  box-shadow:var(--glow-green);
}
.iskg-toggle-text { font-size:11px; color:var(--text); }
.iskg-toggle-wrap.disabled { opacity:0.35; cursor:default; pointer-events:none; }

/* ===== STATUSBAR ===== */
.iskg-statusbar {
  display:flex; align-items:center; gap:12px;
  padding:4px 8px;
  background:var(--bg-panel);
  border-top:1px solid var(--border);
  font-size:10px; font-family:var(--font-mono);
  min-height:22px;
}
.iskg-statusbar-section {
  display:flex; align-items:center; gap:4px;
  color:var(--text-dim);
}
.iskg-statusbar-section .iskg-indicator-dot { width:6px; height:6px; }

/* ===== MENUBAR ===== */
.iskg-menubar {
  display:flex; flex-direction:row; align-items:center;
  background:var(--bg-panel); border:1px solid var(--border);
  border-radius:3px; padding:2px 4px; gap:2px;
  min-height:24px; font-size:11px;
}
.iskg-menubar-item {
  padding:2px 8px; cursor:pointer; border-radius:2px;
  color:var(--text); font-family:var(--font-mono);
}
.iskg-menubar-item:hover { background:var(--border); color:var(--cyan); }
.iskg-menu-dd {
  position:absolute; top:100%; left:0; z-index:1000;
  min-width:160px; display:none;
  background:var(--bg-panel); border:1px solid var(--border);
  border-radius:4px; padding:4px 0;
  box-shadow:0 4px 16px rgba(0,0,0,0.6);
}
.iskg-menu-item {
  display:flex; align-items:center; gap:6px;
  padding:3px 10px; cursor:pointer; color:var(--text);
  font-size:11px; font-family:var(--font-mono); position:relative;
}
.iskg-menu-item:hover { background:var(--cyan-dim); color:var(--cyan); }
.iskg-menu-sub { padding-right:4px; }
.iskg-menu-sub > .iskg-menu-dd {
  position:absolute; top:0; left:100%; margin-left:2px;
}
.iskg-menu-sep { height:1px; margin:3px 8px; background:var(--border); }
.iskg-menu-sc { margin-left:auto; color:var(--text-dim); font-size:9px; }
.iskg-menu-ico { font-size:12px; }

/* ===== SPACER ===== */
.iskg-spacer { min-height:0; min-width:0; }

/* ===== IMAGE BOX ===== */
.iskg-imagebox {
  display:flex; align-items:center; justify-content:center;
  overflow:hidden; position:relative;
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:var(--radius);
}
.iskg-imagebox img {
  width:100%; height:100%;
}

/* ===== ICON LABEL ===== */
.iskg-iconlabel {
  display:inline-flex; align-items:center; gap:6px;
  font-size:11px; color:var(--text);
}
.iskg-icon {
  display:inline-flex; align-items:center; justify-content:center;
  flex-shrink:0;
}
.iskg-icon svg { display:block; }

/* ===== RICH TEXT ===== */
.iskg-richtext-wrap {
  display:flex; flex-direction:column;
  border:1px solid var(--border);
  border-radius:var(--radius);
  overflow:hidden;
}
.iskg-richtext-toolbar {
  display:flex; gap:2px; padding:3px;
  background:var(--bg-panel);
  border-bottom:1px solid var(--border);
  flex-wrap:wrap;
}
.iskg-richtext-toolbar button {
  background:var(--bg-panel-alt); color:var(--text);
  border:1px solid var(--border); border-radius:1px;
  padding:2px 6px; font-size:10px; cursor:pointer;
  font-family:var(--font-mono); line-height:1.2;
  min-width:22px; text-align:center;
  transition:all var(--transition-speed);
}
.iskg-richtext-toolbar button:hover { background:var(--bg-panel-hi); border-color:var(--green); }
.iskg-richtext-toolbar button:active { transform:scale(0.92); }
.iskg-richtext-toolbar button.active { background:var(--green-dim); color:var(--green); border-color:var(--green); }
.iskg-rt-sep {
  display:inline-block; width:1px; height:14px;
  background:var(--border); margin:0 3px; align-self:center;
}
.iskg-richtext-editor {
  flex:1; padding:6px; font-size:11px;
  font-family:var(--font-mono); color:var(--text);
  background:var(--bg-primary);
  outline:none; overflow-y:auto;
  min-height:60px;
}
.iskg-richtext-editor:focus { border-color:var(--cyan); }

/* ===== TREE VIEW ===== */
.iskg-tree {
  display:flex; flex-direction:column;
  font-size:11px; font-family:var(--font-mono);
  background:var(--bg-panel-alt);
  border:1px solid var(--border);
  border-radius:var(--radius);
  overflow:auto;
}
.iskg-tree ul { list-style:none; padding-left:16px; margin:0; }
.iskg-tree > ul { padding-left:0; }
.iskg-tree li { padding:1px 0; }
.iskg-tree-node {
  display:flex; align-items:center; gap:4px;
  padding:2px 4px; cursor:pointer; border-radius:1px;
  color:var(--text);
}
.iskg-tree-node:hover { background:var(--bg-panel-hi); }
.iskg-tree-node.selected { background:var(--cyan-dim); color:var(--cyan); }
.iskg-tree-toggle {
  width:10px; text-align:center; flex-shrink:0;
  color:var(--text-dim); font-size:8px; cursor:pointer;
}
.iskg-tree-icon { width:12px; text-align:center; flex-shrink:0; color:var(--amber); font-size:10px; }
.iskg-tree-text { flex:1; white-space:nowrap; }
.iskg-tree-children { display:none; }
.iskg-tree-children.open { display:block; }

/* ===== DROP TARGET ===== */
.iskg-droptarget {
  display:flex; align-items:center; justify-content:center;
  flex-direction:column; gap:8px;
  background:var(--bg-panel-alt);
  border:2px dashed var(--border-light);
  border-radius:var(--radius);
  color:var(--text-dim); font-size:11px;
  transition:all var(--transition-speed);
  cursor:pointer;
}
.iskg-droptarget.dragover {
  border-color:var(--green);
  background:var(--green-dim);
  color:var(--green);
}
.iskg-droptarget-icon { font-size:24px; }
.iskg-droptarget-text { font-size:10px; }

/* ===== TOOLTIP ===== */
.iskg-tooltip {
  position:fixed; z-index:20000;
  background:var(--bg-panel-hi);
  border:1px solid var(--border-light);
  border-radius:2px;
  padding:4px 8px;
  font-size:10px; font-family:var(--font-mono);
  color:var(--text);
  pointer-events:none;
  white-space:nowrap;
  box-shadow:0 2px 8px rgba(0,0,0,0.4);
}
"""
