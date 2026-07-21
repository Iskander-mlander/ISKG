#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import iskg
from iskg.themes import available_themes

app = iskg.Application(
    title="ISKG Demo - Widget Toolkit",
    width=1100,
    height=900,
    scanlines=True,
    vignette=True,
)

# ── TITLE ──
iskg.Label(
    parent=None,
    text="ISKG v" + iskg.VERSION,
    color="green",
    font_size=18,
    font_family="Orbitron",
)

# ── MenuBar ──
mb = iskg.MenuBar(parent=None)
app.add(mb)

m_file = mb.add_menu("File")
m_file.add_item("New", shortcut="Ctrl+N", command=lambda: print("[Menu] New"))
m_file.add_item(
    "Open...",
    shortcut="Ctrl+O",
    command=lambda: print(f"[FileDialog] {iskg.FileDialog.open_file(app)}"),
)
m_file.add_separator()
m_recent = m_file.add_menu("Recent")
m_recent.add_item("Project A")
m_recent.add_item("Project B")
m_recent.add_separator()
m_recent.add_item("Clear Recent")
m_file.add_separator()
m_file.add_item("Exit", shortcut="Alt+F4", command=lambda: app.quit())

m_edit = mb.add_menu("Edit")
m_edit.add_item("Undo", shortcut="Ctrl+Z")
m_edit.add_item("Redo", shortcut="Ctrl+Y")
m_edit.add_separator()
m_edit.add_item(
    "Open Folder",
    command=lambda: print(f"[FileDialog] {iskg.FileDialog.open_folder(app)}"),
)

m_view = mb.add_menu("View")
m_view.add_item(
    "Toggle Scanlines",
    command=lambda: app.execute_js(
        'document.getElementById("iskg-scanlines").style.display='
        '(document.getElementById("iskg-scanlines").style.display==="none"?"":"none");'
    ),
)
m_view.add_item(
    "Fullscreen",
    command=lambda: app.execute_js(
        "document.documentElement.requestFullscreen?.()||document.documentElement.webkitRequestFullscreen?.()"
    ),
)
m_view.add_separator()

# ── Theme menu ──
m_theme = m_view.add_menu("Theme")
for tname in available_themes():
    m_theme.add_item(
        tname.capitalize(),
        command=lambda n=tname: app.set_theme(n),
    )

m_help = mb.add_menu("Help")
m_help.add_item(
    "About ISKG",
    command=lambda a=app: iskg.MessageDialog(
        title="ABOUT ISKG",
        text=f"Version {iskg.VERSION}\n{len(iskg.__all__)} widgets\nIFAZ Tactical Theme",
        buttons=["OK"],
    ).show(app=a),
)

# ── Main scrollable container ──
main = iskg.Frame(parent=None)
main.config(padding=0, margin=0)
app.add(main)


def hrow(parent, items, gap=8):
    div = iskg.Frame(parent=parent)
    return div


# Tooltip helper: collects JS to execute on startup
_tooltip_js = []


def tt(widget, text, delay=300):
    t = iskg.Tooltip(parent=None, text=text, delay=delay)
    _tooltip_js.append(t.attach(widget.widget_id))


# ════════════════════════════════════════════
# ROW 1 — Buttons, Inputs, Selection
# ════════════════════════════════════════════
row1 = hrow(main, [])
frm_buttons = iskg.Frame(parent=row1, text="Buttons")


def on_btn_click(msg):
    print(f"[ISKG] Button clicked: {msg}")


b1 = iskg.Button(parent=frm_buttons, text="Primary", command=lambda: on_btn_click("Primary"))
tt(b1, "Primary action button")
iskg.Button(
    parent=frm_buttons,
    text="Danger",
    variant="danger",
    command=lambda: on_btn_click("Danger"),
)
iskg.Button(
    parent=frm_buttons,
    text="Caution",
    variant="caution",
    command=lambda: on_btn_click("Caution"),
)
iskg.Button(parent=frm_buttons, text="Disabled", disabled=True)
b_js = iskg.Button(
    parent=frm_buttons, text="Run JS", command=lambda: app.execute_js('alert("Hello!")')
)
tt(b_js, "Execute arbitrary JavaScript")
b_msg = iskg.Button(
    parent=frm_buttons,
    text="Msg Box",
    command=lambda a=app: iskg.MessageDialog(
        title="INFO", text="Message from ISKG.", buttons=["OK", "Cancel"]
    ).show(app=a),
)
tt(b_msg, "Show a modal message dialog")
b_file = iskg.Button(
    parent=frm_buttons,
    text="Open File",
    command=lambda: print(f"[FileDialog] {iskg.FileDialog.open_file(app)}"),
)
tt(b_file, "Native OS file picker")
b_folder = iskg.Button(
    parent=frm_buttons,
    text="Open Folder",
    command=lambda: print(f"[FileDialog] {iskg.FileDialog.open_folder(app)}"),
)
tt(b_folder, "Native OS folder picker")

frm_entry = iskg.Frame(parent=row1, text="Inputs")
iskg.Label(parent=frm_entry, text="Name:")
entry_name = iskg.Entry(parent=frm_entry, text="", placeholder="Enter your name")
tt(entry_name, "Text input field")


def on_name_change(val):
    print(f"[ISGK] Name changed: {val}")


entry_name.bind("change", lambda ev, d=entry_name: on_name_change(d.text))
iskg.Label(parent=frm_entry, text="Password:")
iskg.Entry(parent=frm_entry, text="", placeholder="********", password=True)
iskg.Label(parent=frm_entry, text="Count:")
sp = iskg.SpinBox(parent=frm_entry, from_=0, to=50, value=10)
tt(sp, "Spin box: adjust with buttons or scroll")

frm_sel = iskg.Frame(parent=row1, text="Selection")
cb1 = iskg.CheckBox(parent=frm_sel, text="Enable logging", checked=True)
tt(cb1, "Toggle checkbox on/off")
cb2 = iskg.CheckBox(parent=frm_sel, text="Auto-sync")


def on_check_change(val):
    print(f"[ISGK] Check changed: {val}")


cb1.bind("change", lambda ev, d=cb1: on_check_change(d.checked))
iskg.RadioButton(parent=frm_sel, text="Option A", value="a")
iskg.RadioButton(parent=frm_sel, text="Option B", value="b")
iskg.RadioButton(parent=frm_sel, text="Option C", value="c")
combo = iskg.ComboBox(parent=frm_sel, values=["Alpha", "Bravo", "Charlie", "Delta"], current=0)
tt(combo, "Select from dropdown")


def on_combo_change(val):
    print(f"[ISGK] Combo selected index: {val}")


combo.bind("change", lambda ev, d=combo: on_combo_change(d.current))

# ════════════════════════════════════════════
# ROW 2 — Sliders, Progress, Knobs
# ════════════════════════════════════════════
row2 = hrow(main, [])

frm_slider = iskg.Frame(parent=row2, text="Controls")
slider = iskg.Slider(parent=frm_slider, from_=0, to=100, value=65, width=140)
tt(slider, "Drag or scroll to adjust")


def on_slider_change(val):
    print(f"[ISGK] Slider value: {val}")


slider.bind("change", lambda ev, d=slider: on_slider_change(d.value))
sv = iskg.Slider(parent=frm_slider, from_=0, to=100, value=42, orient="vertical", height=60)
tt(sv, "Vertical slider with scroll support")

frm_prog = iskg.Frame(parent=row2, text="Progress")
pg = iskg.ProgressBar(parent=frm_prog, value=67, width=220, show_text=True)
tt(pg, "Progress indicator")
lb = iskg.ListBox(
    parent=frm_prog,
    items=["Item Alpha", "Item Bravo", "Item Charlie", "Item Delta", "Item Echo"],
    width=220,
    height=90,
)
tt(lb, "Click an item to select")


def on_list_select(idx):
    print(f"[ISGK] List selected index: {idx}")


lb.bind("change", lambda ev, d=lb: on_list_select(ev))

frm_knob = iskg.Frame(parent=row2, text="Knobs")


def on_knob_change(val):
    print(f"[ISGK] Knob: {val}")


knob1 = iskg.Knob(parent=frm_knob, from_=0, to=100, value=65, size=55, color="cyan")
tt(knob1, "Drag in circle to adjust value")
knob1.bind("change", lambda ev, d=knob1: on_knob_change(d.value))
iskg.Knob(parent=frm_knob, from_=0, to=10, value=3, size=50, color="green")
iskg.Knob(parent=frm_knob, from_=0, to=100, value=80, size=50, color="amber")

# ════════════════════════════════════════════
# ROW 3 — LED, Indicators, Toggles
# ════════════════════════════════════════════
row3 = hrow(main, [])

frm_led = iskg.Frame(parent=row3, text="LED Displays")
led_rpm = iskg.LEDDisplay(
    parent=frm_led, value=42, digits=3, color="green", label="RPM", height=34
)
led_alarms = iskg.LEDDisplay(
    parent=frm_led, value=1984, digits=4, color="red", label="ALARMS", height=30
)
led_volts = iskg.LEDDisplay(
    parent=frm_led, value=314, digits=4, color="amber", label="VOLTS", height=28
)

frm_indi = iskg.Frame(parent=row3, text="Indicators")
il1 = iskg.IndicatorLED(parent=frm_indi, color="green", size=8, active=True, label="Online")
tt(il1, "Online indicator")
iskg.IndicatorLED(parent=frm_indi, color="red", size=8, active=False, label="Alarm")
iskg.IndicatorLED(parent=frm_indi, color="amber", size=8, active=True, label="Warning")
iskg.IndicatorLED(parent=frm_indi, color="cyan", size=8, active=True, label="Link")
iskg.IndicatorLED(parent=frm_indi, color="blue", size=6, active=False, label="Off")

frm_toggle = iskg.Frame(parent=row3, text="Toggles")


def on_toggle(val):
    print(f"[ISGK] Toggle: {val}")


tog1 = iskg.ToggleSwitch(parent=frm_toggle, text="Master Arm", checked=True)
tt(tog1, "Toggle switch on/off")
tog1.bind("change", lambda ev, d=tog1: on_toggle(d.checked))
iskg.ToggleSwitch(parent=frm_toggle, text="NV Mode", checked=False)
iskg.ToggleSwitch(parent=frm_toggle, text="Auto Track", checked=True)

# ════════════════════════════════════════════
# ROW 4 — Scale, Scrollbars, Text
# ════════════════════════════════════════════
row4 = hrow(main, [])

frm_scale = iskg.Frame(parent=row4, text="Scale")
sc = iskg.Scale(parent=frm_scale, from_=0, to=100, value=50, width=160)
tt(sc, "Drag or scroll to adjust")


def on_scale_change(val):
    print(f"[ISGK] Scale: {val}")


sc.bind("change", lambda ev, d=sc: on_scale_change(d.value))

frm_scroll = iskg.Frame(parent=row4, text="Scrollbars")
sb_h = iskg.ScrollBar(parent=frm_scroll, orient="vertical", value=30, height=70)
tt(sb_h, "Scroll with mouse wheel")
iskg.ScrollBar(parent=frm_scroll, orient="horizontal", value=50, width=100)

txt = iskg.Text(
    parent=iskg.Frame(parent=row4, text="Log"),
    text="[ISKG] System initialized.\n[ISKG] Ready.",
    width=260,
    height=70,
)
tt(txt, "Multi-line text area")

# ════════════════════════════════════════════
# ROW 5 — DataGrid, Canvas
# ════════════════════════════════════════════
row5 = hrow(main, [])

dg = iskg.DataGrid(
    parent=row5,
    columns=["TARGET", "STATUS", "PRIORITY", "ETA"],
    rows=[
        ["Site A", "Active", "High", "12:45"],
        ["Site B", "Standby", "Low", "14:00"],
        ["Site C", "Alert", "Critical", "Now"],
        ["Site D", "Active", "Medium", "15:30"],
        ["Site E", "Offline", "Low", "—"],
    ],
    width=460,
    height=130,
)
tt(dg, "Click column header to sort")


def on_grid_select(row_idx):
    print(f"[ISGK] Grid selected row: {row_idx}")


dg.bind("select", on_grid_select)

cv = iskg.Canvas(parent=iskg.Frame(parent=row5, text="Canvas"), width=240, height=110)
cv.create_rectangle(10, 10, 90, 50, fill="#0f2e1a", outline="#4ade80")
cv.create_oval(110, 10, 180, 50, fill="#0a2030", outline="#22d3ee")
cv.create_line(10, 70, 230, 90, color="#f59e0b", width=2)
cv.create_text(120, 65, text="ISKG Canvas", fill="#c8d6e5", font="11px Orbitron", anchor="center")
tt(cv, "Drawing canvas with shapes")

# ════════════════════════════════════════════
# ROW 6 — Gauges, Notebook
# ════════════════════════════════════════════
row6 = hrow(main, [])

gauge_signal = iskg.RadialGauge(
    parent=iskg.Frame(parent=row6, text="Radial Gauges"),
    from_=0,
    to=100,
    value=72,
    size=75,
    label="SIGNAL",
    units="%",
)
gauge_rpm = iskg.RadialGauge(
    parent=row6._children[-1], from_=0, to=3500, value=2200, size=75, label="RPM"
)
gauge_fuel = iskg.RadialGauge(
    parent=row6._children[-1],
    from_=0,
    to=100,
    value=35,
    size=75,
    label="FUEL",
    units="%",
)

nb = iskg.Notebook(parent=row6)
nb.add_tab("Tab 1", iskg.Label(parent=nb, text="Content of Tab 1", color="green"))
nb.add_tab("Tab 2", iskg.Label(parent=nb, text="Content of Tab 2", color="cyan"))
nb.add_tab("Tab 3", iskg.Label(parent=nb, text="Content of Tab 3", color="amber"))
nb.config(width=240, height=100)
tt(nb, "Click tabs to switch")

# ════════════════════════════════════════════
# ROW 7 — Custom styles
# ════════════════════════════════════════════
row7 = hrow(main, [])


def on_custom_css():
    app.execute_js(
        'document.body.style.background = "radial-gradient(ellipse at 50% 50%, rgba(74,222,128,0.1), #070b10)";'
    )


iskg.Button(parent=row7, text="Custom Theme", variant="caution", command=on_custom_css)

iskg.Label(
    parent=iskg.Frame(parent=row7, text="Style Config"),
    text="fg=red, bg=#111:",
    fg="red",
    bg="#111",
    padding=4,
)
iskg.Button(parent=row7._children[-1], text="fg=cyan, bg=#0a2030", fg="#22d3ee", bg="#0a2030")
iskg.Entry(
    parent=row7._children[-1],
    text="fg=green, bg=#040810",
    fg="#4ade80",
    bg="#040810",
    width=180,
)

# ════════════════════════════════════════════
# ROW 8 — Image, Icons, RichText, Tree, Drop
# ════════════════════════════════════════════
row8 = hrow(main, [])

import urllib.parse, os

_radar_svg = "data:image/svg+xml," + urllib.parse.quote(
    open(os.path.join(os.path.dirname(__file__), "radar.svg")).read()
)
img = iskg.ImageBox(
    parent=iskg.Frame(parent=row8, text="ImageBox"),
    src=_radar_svg,
    width=80,
    height=60,
    fit="contain",
)
tt(img, "Image display from SVG data URI")

frm_icons = iskg.Frame(parent=row8, text="IconLabels")
iskg.IconLabel(parent=frm_icons, text="Armed", icon="⚡", icon_size=14, color="red")
iskg.IconLabel(parent=frm_icons, text="Secure", icon="🔒", icon_size=12, color="green")
iskg.IconLabel(
    parent=frm_icons,
    text="Signal",
    icon=(
        '<svg viewBox="0 0 16 16" width="14" height="14"><path d="M8 1a7 7 0 0 0-7 7h2a5 5 0 0 1 5-5V1z" fill="#4ade80"/>'
        '<path d="M8 4a4 4 0 0 0-4 4h2a2 2 0 0 1 2-2V4z" fill="#4ade80"/><circle cx="8" cy="11" r="1.5" fill="#22d3ee"/></svg>'
    ),
    icon_size=14,
    color="cyan",
)
iskg.IconLabel(parent=frm_icons, text="Warning", icon="⚠", icon_size=14, color="amber")

rt = iskg.RichText(
    parent=iskg.Frame(parent=row8, text="RichText", width=240),
    text="<b>Bold</b> <i>Italic</i> <u>Underline</u><br><span style='color:#22d3ee'>Cyan text</span> <span style='color:#f59e0b'>Amber</span>",
    height=120,
)
tt(rt, "Rich text editor with toolbar")

tv = iskg.TreeView(
    parent=iskg.Frame(parent=row8, text="TreeView"),
    items=[
        {
            "text": "Sensors",
            "icon": "📡",
            "open": True,
            "children": [
                {"text": "Radar A", "icon": "📡"},
                {"text": "Radar B", "icon": "📡"},
                {"text": "IR Array", "icon": "🔭"},
            ],
        },
        {
            "text": "Comms",
            "icon": "📻",
            "children": [
                {"text": "UHF 1", "icon": "📻"},
                {"text": "UHF 2", "icon": "📻"},
                {"text": "SatLink", "icon": "🛰"},
            ],
        },
        {
            "text": "Power",
            "icon": "🔋",
            "children": [{"text": "Main", "icon": "⚡"}, {"text": "Aux", "icon": "⚡"}],
        },
        {"text": "Logs", "icon": "📋"},
    ],
    width=180,
    height=120,
)
tt(tv, "Click to expand/collapse; click node to select")

dt = iskg.DropTarget(
    parent=iskg.Frame(parent=row8, text="DropTarget"),
    text="Drop files",
    width=120,
    height=80,
)
tt(dt, "Drag and drop files here")

# ════════════════════════════════════════════
# Footer
# ════════════════════════════════════════════
iskg.Separator(parent=None, orient="horizontal", width="95%")

frm_bottom = iskg.Frame(parent=None)
frm_bottom._config_dict["flex"] = "0 0 auto"
app.add(frm_bottom)

iskg.StatusBar(
    parent=frm_bottom,
    sections=[
        {"text": "COM: ACTIVE", "color": "green"},
        {"text": "SYS: NOMINAL", "color": "cyan"},
        {"text": f"v{iskg.VERSION}", "color": "dim"},
    ],
)
iskg.Label(
    parent=frm_bottom,
    text=f"{len(iskg.__all__)} widgets | IFAZ",
    color="dim",
    font_size=9,
)

# ── RUN ──
if __name__ == "__main__":
    print("Starting ISKG Demo...")
    _anim_js = f"""(function(){{
  function ra(a,b){{return a+Math.random()*(b-a);}}
  var c={{sg:72,rp:2200,fu:35}},tg={{}};
  function pick(k){{
    if(k=='rp')tg.rp=ra(200,3300);
    else if(k=='sg')tg.sg=ra(10,90);
    else tg.fu=ra(5,95);
  }}
  pick('rp');pick('sg');pick('fu');
  setInterval(function(){{
    ['rp','sg','fu'].forEach(function(k){{
      var d=tg[k]-c[k],sp=k=='rp'?60:k=='sg'?1.5:0.8;
      if(Math.abs(d)<sp*2)pick(k);
      c[k]+=Math.sign(d)*Math.min(Math.abs(d),sp);
    }});
    var fn;
    fn=window.iskg_gauge_{gauge_signal.widget_id};if(fn)fn(c.sg);
    fn=window.iskg_gauge_{gauge_rpm.widget_id};if(fn)fn(c.rp);
    fn=window.iskg_gauge_{gauge_fuel.widget_id};if(fn)fn(c.fu);
    [['{led_rpm.widget_id}',3,999],['{led_alarms.widget_id}',4,9999],['{led_volts.widget_id}',4,9999]].forEach(function(x){{
      var el=document.getElementById(x[0]);if(!el)return;
      var n=(parseInt(el.getAttribute('dv')||'0')+1)%x[2];el.setAttribute('dv',n);
      el.querySelector('.iskg-led-digits').innerText=String(n).padStart(x[1],'0');
    }});
  }},60);
}})();"""
    sys.exit(app.run(extra_js=";".join(_tooltip_js + [_anim_js])))
