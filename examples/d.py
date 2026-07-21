#!/usr/bin/env python3
"""ISKG dashboard demo — showcases widget interaction."""

from iskg import (
    Application,
    Button,
    Label,
    Frame,
    Knob,
    LEDDisplay,
    Slider,
    ComboBox,
    ToggleSwitch,
    Separator,
    IndicatorLED,
)

app = Application(title="ISKG Dashboard", width=680, height=480)

counter = 0


# ── callbacks ──────────────────────────────────────────────
# command=... calls with NO args; bind("change",...) passes data
def on_knob(data):
    led.value = int(float(data))


def on_slider():
    throttle_led.value = int(slider.value)
    slider_val.config(text=f"{slider.value:.0f}%")
    ind_led.active = slider.value > 50


def on_arm():
    global counter
    counter += 1
    status_lbl.config(text=f"Armed x{counter}")
    indicator_lbl.config(text="● ARMED", fg="#4ade80")


def on_disarm():
    status_lbl.config(text="Standing By")
    indicator_lbl.config(text="● SYSTEM IDLE", fg="#555")


def on_theme(data=None):
    app.set_theme(combo.value)


# ── root grid ──────────────────────────────────────────────
root = Frame()
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)

# ── title row ──────────────────────────────────────────────
Label(parent=root, text="ISKG DASHBOARD", anchor="center", font="bold 16px").grid(
    row=0, column=0, columnspan=2, sticky="we", padx=8, pady=8
)

Separator(parent=root, orient="horizontal").grid(
    row=1, column=0, columnspan=2, sticky="we", pady=2
)

# ── left panel: Knob + LED ─────────────────────────────────
left = Frame(parent=root)
left.grid(row=2, column=0, sticky="nsew", padx=10, pady=6)

Label(parent=left, text="RPM CONTROL", anchor="center", font="bold 12px").grid(
    row=0, column=0, sticky="we", pady=8
)

knob = Knob(parent=left, from_=0, to=3000, value=0, size=90, color="cyan")
knob.bind("change", on_knob)
knob.grid(row=1, column=0, sticky="c", pady=6)

led = LEDDisplay(parent=left, value=0, digits=4, color="cyan", height=38)
led.grid(row=2, column=0, sticky="c", pady=8)

Label(parent=left, text="revolutions / min", anchor="center", fg="#667").grid(
    row=3, column=0, sticky="we", pady=4
)

# ── right panel: Slider + ProgressBar ──────────────────────
right = Frame(parent=root)
right.grid(row=2, column=1, sticky="nsew", padx=10, pady=6)

Label(parent=right, text="THROTTLE", anchor="center", font="bold 12px").grid(
    row=0, column=0, sticky="we", pady=8
)

slider = Slider(parent=right, from_=0, to=100, value=0, command=on_slider)
slider.grid(row=1, column=0, sticky="we", pady=12)

throttle_led = LEDDisplay(parent=right, value=0, digits=3, color="amber", height=36)
throttle_led.grid(row=2, column=0, sticky="c", pady=4)

Label(parent=right, text="engine load %", anchor="center", fg="#667").grid(
    row=3, column=0, sticky="we", pady=4
)
slider_val = Label(parent=right, text="0%", anchor="center", font="bold 14px")
slider_val.grid(row=4, column=0, sticky="we", pady=2)

ind_led = IndicatorLED(parent=right, color="red")
ind_led.grid(row=5, column=0, sticky="c", pady=4)

indicator_lbl = Label(parent=right, text="● SYSTEM IDLE", anchor="center", fg="#555")
indicator_lbl.grid(row=6, column=0, sticky="we", pady=4)
# ── bottom separator ───────────────────────────────────────
Separator(parent=root, orient="horizontal").grid(
    row=3, column=0, columnspan=2, sticky="we", pady=4
)

# ── bottom bar: controls ──────────────────────────────────
bottom = Frame(parent=root)
bottom.grid(row=4, column=0, columnspan=2, sticky="we", padx=10, pady=6)
bottom.grid_columnconfigure(0, weight=1)
bottom.grid_columnconfigure(1, weight=1)

# left group: status + buttons
left_grp = Frame(parent=bottom)
left_grp.grid(row=0, column=0, sticky="w")

status_lbl = Label(parent=left_grp, text="Standing By")
status_lbl.grid(row=0, column=0, padx=4)

Button(parent=left_grp, text="ARM", width=70, command=on_arm).grid(row=0, column=1, padx=4)

Button(parent=left_grp, text="DISARM", width=70, command=on_disarm).grid(row=0, column=2, padx=4)

# right group: theme selector + toggle
right_grp = Frame(parent=bottom)
right_grp.grid(row=0, column=1, sticky="e")

Label(parent=right_grp, text="Theme:").grid(row=0, column=0, padx=4)

combo = ComboBox(
    parent=right_grp,
    values=["ifaz", "cold", "warm", "night"],
    current=0,
    command=on_theme,
)
combo.grid(row=0, column=1, padx=4)

ToggleSwitch(parent=right_grp).grid(row=0, column=2, padx=8)

app.add(root)
app.run()
